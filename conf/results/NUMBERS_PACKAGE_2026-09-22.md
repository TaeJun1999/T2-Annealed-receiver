<!-- 원고용 검증 숫자 패키지.  4 검증자 + 판정자 워크플로(wf_b69bb0d7-06e)가 소스 파일에 대조해 조립.
     이 파일은 conf/ 의 정본을 대체하지 않는다 -- 인용 시 'source' 열의 파일을 다시 연다.
     PENDING 표시: B16e4(게이트 통과 + 동일예산), 시드 a3, §6p 저SNR, K=1024@4e4/1.6e5, λ 스윕.
     교차검증 X1/X6/X10/X14/X15 는 14:40 에 STATUS.md 와 F12 에 반영했다. -->

# VERIFIED NUMBERS PACKAGE — Stage C, D1/D2

**Assembled** 2026-09-22 from four independent verifier passes, cross-checked against the source files. Read-only; nothing was created, modified or re-run.

**Citation rule in force** (`conf/STATUS.md`, "인용 규칙"): every number carries (i) n, (ii) testbed / cell / SNR, (iii) gate status, (iv) equal-budget status, (v) power verdict. A number missing any of the five is marked **NOT QUOTABLE** below.

**Precedence rule applied throughout: the source file wins over STATUS.md.** Where two verifiers disagreed I opened the source file myself; the ruling is recorded inline as `[CROSS-CHECKED]`.

---

## 0. CROSS-CHECK LEDGER — where the four verifiers disagreed, and who was right

| # | Disagreement | Ruling | Source I read |
|---|---|---|---|
| X1 | **C1 / −3 dB BLER in the equal-budget run.** V1+V2 said BLER = 1.000 / 1.000 / 0.996 for V0/V1/V4 with BER = nan. V4 said "BLER = nan (every trial terminated by exception)". | **V1+V2 right, V4 wrong.** TABLE A reads `M-ours-dscore-C-V0 1.000(0.999,1.000) nan 2.59e+01`, `V1 1.000(0.999,1.000) nan 2.63e+05`, `V4 0.996(0.993,0.998) nan 1.92e+22`. Detail rows give BLER@1/@2/@8/@16 = 1.000 1.000 1.000 1.000 for V0 and V1. It is **BER@16, `ok=`, `tauL@1` that are nan — not BLER**. Header NOTEs: V0 970/2560, V1 804/2560, V4 136/2560 non-finite blocks **KEPT and counted as block errors, never dropped**. | `/home/HTJ/t2/conf/results/tables_D2_B1e4x.txt:54-56, :73-79, :91-94` |
| X2 | **V4b BLER on C5 at −3 dB.** V1 said 0.988; V2 said 0.993 (0.988, 0.995). | **V1 right.** C5 −3 dB V4b = **0.988 (0.982, 0.991)**, NMSE 3.58e+16. V2 transcribed C1's **+0 dB** cell (0.993 (0.988, 0.995), NMSE 1.27e+17). | `tables_D2_B1e4x.txt:293` (C5), `:77` (C1) |
| X3 | **V4b median NMSE on C5.** V2 said "~1–2e17". | **Wrong.** C5 V4b NMSE median is **3.58e+16 – 3.63e+16** across the 7 SNRs. C1 V4b is 1.27e+17 – 1.28e+17. (The ~1e17–5e17 figures V1 quoted are *worst-case* NMSE from the guard file, a different quantity.) | `tables_D2_B1e4x.txt:77, :293`; `guard_D2_B1e4x.txt` |
| X4 | **V4b C2 −3 dB BLER: 0.161 or 0.162?** | **Both are real, in different tables.** Equal-budget N=1e4: **0.162 (0.148, 0.176)**. Non-equal-budget N=1.6e5: **0.161 (0.148, 0.176)**. STATUS §6f discusses the equal-budget run, so 0.162 is the right number *there*; 0.161 is not an error, it is the other table. | `tables_D2_B1e4.txt:73`; `tables_D2_C.txt:294` |
| X5 | **V4b's budget line.** V1+V4 said code wins (V4b is built from the learned `score_prior_c`). V3 said "the table's own header is the file of record and it says 10000." | **V1+V4 right, V3 wrong.** `arms.py` builds V4b from the *same* `score_prior_c` object as V0/V1/V4. `runner.py` prints `N_train={ntrain} -- unclassified arm` because V4b is in none of the classifier's name lists — a classifier gap, not a measurement. Consequence: in the equal-budget tables the printed 10000 happens to equal the true budget; **in `tables_D2_C.txt` the printed 10000 is wrong — V4b's budget there is N_train=1.6e5.** | `/home/HTJ/t2/conf/code/arms.py:172-179`; `/home/HTJ/t2/conf/code/runner.py:245-258`; `tables_D2_B1e4.txt:40` |
| X6 | **F3 guard, C1 / −3 dB, V4.** STATUS says 2560/2560 for V0, V1 *and* V4 together. | **Source wins: V4 = 2552/2560 = 0.997** (worst NMSE 1.815e+28). V0 = 2560/2560 (2.097e+17), V1 = 2560/2560 (4.153e+23), V4b = 2560/2560 (4.734e+17). | `guard_D2_B1e4x.txt:18-22` |
| X7 | **D1 guard, C1 / −3 dB.** STATUS.md:181 says "1400/1400", V1 worst 6.6e+17. | **Source wins: 2560/2560 for V0, V1 and V4; V1 worst NMSE = 1.654e+20**, not 6.6e+17 (2.5 orders out). The string "1400" appears in no guard file. V0 also fires 11/2560 (0.004) at C1 **+3 dB**, worst 3.625e+05 — STATUS omits that row. | `guard_D1_C.txt:18-21` |
| X8 | **N=1.6e5 GMM fit set — which files are missing.** V3+V4 said "Nr=8 kron K=128 **and Nr=8 full K=256** absent". | **Half wrong.** As of my read the Nr=8 **full** family is complete (K=16…512). Only **Nr=8 kron K=128** is missing. Nr=4 is missing kron K=64/128/256. | `ls /home/HTJ/t2/conf/results/gmm_fits_D2_n16e4/` |
| X9 | **HPO trial count: 724 or 959?** | **Genuine source-vs-source conflict, unresolved.** `hpo_D1.txt:16` states `trials : 724 total, 724 completed, 0 failed/infeasible`. `gate_D2.txt:11` and `samplecx_D1.txt:41` both say **959**, and `samplecx_D1.txt:41` explicitly attributes 959 *to hpo_D1.txt*. The 959 banner is copied verbatim into five D2 tables. 724 + 196 (stratified) = 920; + 49 gated ladder rows = 969. **I could not reconstruct 959.** | `hpo_D1.txt:16`; `gate_D2.txt:11`; `samplecx_D1.txt:41`; `tables_D2_B1e4.txt:440` etc. |
| X10 | **K=1024 reseed count: 9372 or 9144?** | **Source wins: 9144.** The `.npz` that holds the quoted `ll_val = -23.5726` is the selected restart, `n_reseed = 9144`, `cand_ll_val = [-23.8329, -24.0051, -23.5726]`. 9372 is restart 0's count, and restart 0 was not selected. | `gmm_fits_D2_K1024/fit_S2_Nr8_kronK1024_n10000.npz` |
| X11 | **Stage A/B n at the decision points.** | **V3 right.** `tables_D2.txt:189` records cell C2 `n per SNR: [2560, 2560, 640, 640, 640, 640, 640]`. So the +3 dB decision point of every C2 pair in that file is **n = 640**, not 2560. | `tables_D2.txt:189` |
| X12 | **`gmmB\|flip4` at n=256.** | Confirmed: n=256 sweep gives **0.4180 at −3 dB, 0.1172 at +0 dB** (against `gmmB\|eta` 0.3008 / 0.0898). The n=64 probe gave 0.141 at 0 dB. Direction preserved, digits do not travel. | `jacpsd_counterfactual_SUMMARY_n256.txt:19` |
| X13 | **Test M6.** | Confirmed absent. `grep -n "M6" results/tests.txt results/tests_VREV.txt` → **no matches**. The pre-registered integrity test that guards V1 has no recorded result. | `results/tests.txt`, `results/tests_VREV.txt` |
| X14 | **σ-coverage file header.** | Confirmed defect: the file self-labels `cell : C1 (8x4 T=16 Tp=4)`. **C1 is Tp=2.** The data are genuinely Tp=2 (measured +15 dB ν_q → 1.015, which is the Tp=2 limit; Tp=4's limit is exactly 0). | `results/diag/sigma-coverage_D2_C1_n8.txt:13` |
| X15 | **σ-coverage "100% out of grid".** | Confirmed: `out of range : 48/48 = 100.0% (below 0, above 48)` and `first it out of range : [0 0 0 1 0 1 0 1]` — only **3 of the nominal 8 trials** contributed a σ_t record (48 = 3 × 16). Control arms at the same point report 8/128. | `results/diag/sigma-coverage_D2_C1_n8.txt:20-22` |

---

# (A) HEADLINE RESULT — full citation block

## A1. Equal-budget C2 (Tp=4), N_train = 1e4: M-ours-bstar → M-ours-dscore-C-V1

> **sign test @16:** −3 dB **323:49** p=1.3e-50 · +0 dB **134:16** p=2.2e-24 · +3 dB **45:7** p=7e-08 · **pooled 502:72 p=2.6e-80**
> **verdict line (verbatim):** `second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant`
> **SNR@0.1 gap (M-ours-bstar minus V1):** **+1.68 dB** [90% paired bootstrap +1.47, +1.94; censored replicates 0%]

| Field | Value |
|---|---|
| **(i) n** | **2560 per SNR point**, 7 points |
| **(ii) testbed / cell / SNR** | **D2** / cell **C2** (8×4, T=16, **Tp=4**, K=42), prior S2 / decision SNRs **−3, +0, +3 dB** (anchor arm **M-ours-bstar**, window BLER ∈ [0.005, 0.9]) |
| **(iii) gate** | **FAIL.** `ckpt/d2sx_N10000_a1.pt`. Table header verbatim: `NO GATE RECORD mentions d2sx_N10000_a1.pt -- UNVERIFIED here. (GA-GD are measurable on D1 only, 10_SPEC §5: a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)` The FAIL is **inherited** from the D1 sibling at the same N_train (`samplecx_D1.txt:28`, GC 0.24333 vs threshold 0.15). §6d re-registered these runs as **budget-axis measurements, not arm results**. |
| **(iv) equal budget** | **YES, N_train = 10000 for both arms** (and for every other fitted arm in the table). |
| **(v) power** | **POWERED** — `3 decision points, 3 with >= 6 discordant pairs` |
| **source** | `/home/HTJ/t2/conf/results/tables_D2_B1e4.txt:367-372`; budget header `:33-42` |

### A2. The point estimates behind it (same five fields as A1)

D2 / C2 (Tp=4) / **−3 dB** / n=2560 / gate FAIL (d2sx_N10000_a1.pt, inherited) / equal budget N=1e4 / **no test — TABLE A point estimates**
Source: `/home/HTJ/t2/conf/results/tables_D2_B1e4.txt:63-77`

| arm | BLER@16 (95% Wilson CI) | BER@16 | NMSE_H |
|---|---|---|---|
| M-ours-dscore-C-V0 | 0.789 (0.772, 0.804) | 3.6e-01 | 2.50e-01 |
| R1-turbo | 0.537 (0.517, 0.556) | 1.9e-01 | 1.99e-01 |
| R2-ours-G | 0.329 (0.311, 0.347) | 1.2e-01 | 1.37e-01 |
| M-ours-gmm32 | 0.276 (0.259, 0.294) | 1.0e-01 | 1.13e-01 |
| M-ours-bstar-scalar | 0.261 (0.244, 0.278) | 9.7e-02 | 1.05e-01 |
| **M-ours-bstar** | **0.252 (0.236, 0.270)** | 9.6e-02 | 1.04e-01 |
| M-ours-dscore-C-V4 | 0.152 (0.139, 0.167) | 5.4e-02 | 5.55e-02 |
| M-ours-dscore-C-V4b | 0.162 (0.148, 0.176) | 5.9e-02 | 5.90e-02 |
| **M-ours-dscore-C-V1** | **0.145 (0.132, 0.159)** | 5.2e-02 | 5.60e-02 |
| R5-genie | 0.034 (0.028, 0.042) | 1.1e-02 | n/a |

**Derived ratios** (same cell/SNR/n/gate/budget; **power = point estimate only**):
- b* → V1: `1 − 0.145/0.252 = 42.5 %` — **−3 dB is one of this pair's three decision SNRs**, so the ratio sits at a decision point, and the pair behind it is POWERED 3/3.
- V0 → V1: `1 − 0.145/0.789 = 81.6 %` — **NO TEST EXISTS** (see E3).
- **Mandatory caveat that must travel with V0's 0.789:** it is an average that **keeps 1822/2560 = 0.712 diverged trials** at this SNR (`guard_D2_B1e4.txt:18`).

---

# (B) SUPPORTING RESULTS

All rows: **D2**, prior S2, **n = 2560 per SNR point**, anchor arm named, `DIVERGE_NMSE = 10.0` reused from `code/bigamp.py`.

## B1. Same comparison, second budget — N_train = 4e4, cell C2 (Tp=4)

| pair | decision SNRs | counts / p | pooled | SNR@0.1 gap | power |
|---|---|---|---|---|---|
| M-ours-bstar → V1 | −3/+0/+3 | 323:52 p=6.6e-49 · 112:13 p=8.1e-21 · 40:5 p=7.9e-08 | **475:70 p=5.8e-75** | +1.45 dB [+1.27, +1.67] | POWERED |
| M-ours-bstar → V4 | −3/+0/+3 | 306:60 · 112:27 · 39:4 | 457:91 p=1.2e-59 | +1.27 dB [+1.08, +1.49] | POWERED |
| M-ours-bstar → V4b | −3/+0/+3 | 302:60 · 104:27 · 38:7 | 444:94 p=2.3e-55 | +1.19 dB [+1.00, +1.41] | POWERED |
| R2-ours-G → V1 | −3/+0/+3 | 510:43 · 188:11 · 82:8 | 780:62 p=5.5e-159 | +2.32 dB [+2.07, +2.58] | POWERED |

**gate:** FAIL — `ckpt/d2sx_N40000_a1.pt`; header `NO GATE RECORD mentions d2sx_N40000_a1.pt -- UNVERIFIED here`; FAIL inherited from the D1 sibling (`samplecx_D1.txt:29`, GC 0.16651 vs 0.15).
**equal budget:** YES, N_train = 40000 for every fitted arm (R3-bigamp N=0; R5-genie n/a).
**source:** `/home/HTJ/t2/conf/results/tables_D2_B4e4.txt:367-384, :337-342`

**TABLE A at −3 dB** (n=2560, no test): V0 0.741 (0.724,0.758) · R1-turbo 0.543 · R2-ours-G 0.327 · bstar-scalar 0.258 · **M-ours-bstar 0.250** · V4b 0.156 · V4 0.154 · **V1 0.145** · genie 0.034. `tables_D2_B4e4.txt:58-76`.
Ratios: b*→V1 = 42.0 %; V0→V1 = 80.4 % (**no test**). V0's 0.741 keeps **1797/2560 = 0.702** diverged trials (`guard_D2_B4e4.txt:19`).

## B2. Cell generalisation — equal budget N=1e4, cells C1 (Tp=2) and C5 (Tp=3)

Source: `/home/HTJ/t2/conf/results/tables_D2_B1e4x.txt`. gate FAIL (d2sx_N10000_a1.pt, inherited GC 0.2433). Equal budget N_train=10000 throughout. n=2560 per SNR. **All POWERED** (3 decision points, 3 with ≥6 discordant pairs) unless stated.

| cell | pair | decision SNRs | per-point | pooled | verdict (verbatim) | line |
|---|---|---|---|---|---|---|
| **C5** (Tp=3) | bstar → **V1** | +9/+12/+15 | 282:170 p=1.5e-07 · 268:221 p=0.037 · **243:276 p=0.16** | 793:667 p=0.0011 | `second arm fewer failures at 2/3 points, first arm fewer failures at 0/3 points -> significant` | `:728-733` |
| C5 | bstar → V4 | +9/+12/+15 | 257:259 p=0.96 · 257:276 p=0.44 · 224:284 p=0.0088 | 738:819 p=0.043 | `second arm fewer failures at 0/3, first arm fewer failures at 1/3 -> not significant` | `:734-739` |
| C5 | bstar → V4b | +9/+12/+15 | 3:2125 · 2:2139 · 2:2156, all p=0 | 7:6420 p=0 | first arm (GMM) 3/3 | `:740-745` |
| C5 | bstar → V0 | +9/+12/+15 | 38:1759 · 67:1428 · 91:1070 p=1.1e-212 | 196:4257 p=0 | first arm (GMM) 3/3 | `:722-727` |
| C5 | R2-ours-G → V1 | +9/+12/+15 | 261:166 p=5e-06 · 213:226 p=0.57 · 187:289 p=3.4e-06 | 661:681 p=0.6 | `1/3 each way -> not significant` | `:698-703` |
| C5 | bstar → bstar-scalar | +9/+12/+15 | 202:317 · 194:325 · 192:327 | 588:969 p=3.7e-22 | matrix-site GMM 3/3 | `:746-751` |
| **C1** (Tp=2) | bstar → **V1** | +6/+12/+15 | **462:473 p=0.74** · 453:530 p=0.015 · 457:629 p=2e-07 | 1372:1632 p=2.3e-06 | `second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points -> significant` — **the GMM wins** | `:588-593` |
| C1 | bstar → V4 | +6/+12/+15 | 456:459 p=0.95 · 484:449 p=0.27 · 499:496 p=0.95 | 1439:1404 p=0.52 | `not significant` | `:594-599` |
| C1 | bstar → V4b | +6/+12/+15 | 1:1517 · 2:1557 · 3:1560, all p=0 | 6:4634 p=0 | first arm (GMM) 3/3 | `:600-605` |
| C1 | bstar → V0 | +6/+12/+15 | 30:1462 p=0 · 68:1316 p=1.5e-300 · 142:1182 p=1.8e-204 | 240:3960 p=0 | first arm (GMM) 3/3 | `:582-587` |
| C1 | R2-ours-G → V1 | +9/+12/+15 | 401:454 p=0.075 · 370:463 p=0.0014 · 336:581 p=5.2e-16 | 1107:1498 p=1.9e-14 | first arm (**R2-ours-G**) 2/3 | `:558-563` |
| C1 | bstar → bstar-scalar | +6/+12/+15 | 330:496 · 377:476 · 410:513 | 1117:1485 p=5.7e-13 | matrix-site GMM 3/3 | `:606-611` |
| C1 | R4-llr → R4-scvamp | +3 only | 243:41 p=4.3e-36 | — | **UNDECIDED** — `1 decision point (needs 3)` | `:528-533` |

**C1 / −3 dB TABLE A** [CROSS-CHECKED, X1] (n=2560, **not a decision point for any C1 pair**): V0 **1.000** (0.999,1.000) BER nan NMSE 2.59e+01 · V1 **1.000** (0.999,1.000) BER nan NMSE 2.63e+05 · V4 **0.996** (0.993,0.998) BER nan NMSE 1.92e+22 · V4b **0.997** (0.994,0.998) BER 5.0e-01 NMSE 1.27e+17 · **M-ours-bstar 0.778** (0.761,0.793) · bstar-scalar 0.798 · R2-ours-G 0.797 · R1-turbo 0.918 · R5-genie 0.037. `tables_D2_B1e4x.txt:73-79`.
Header NOTEs (`:54-56`): non-finite `blk_err@16` blocks — V0 970/2560, V1 804/2560, V4 136/2560 — **KEPT and counted as block errors, never dropped**.

**C5 / −3 dB TABLE A** (n=2560, **not a decision point** for the C5 bstar→V1 pair): V0 0.904 · R1-turbo 0.795 · R2-ours-G 0.610 · bstar-scalar 0.571 · **M-ours-bstar 0.544** · V4 0.419 · **V1 0.394** · **V4b 0.988** (0.982,0.991) [CROSS-CHECKED, X2] · genie 0.036. `tables_D2_B1e4x.txt:284-297`.

**The Tp ordering as measured** (each cell at **its own** anchor-determined decision SNRs — not matched SNRs):

| cell | Tp | pooled bstar → V1 | verdict |
|---|---|---|---|
| C2 | 4 | 502:72 p=2.6e-80 | V1 wins **3/3** |
| C5 | 3 | 793:667 p=0.0011 | V1 wins **2/3** (+15 dB reverses: 243:276 p=0.16) |
| C1 | 2 | 1372:1632 p=2.3e-06 | **GMM wins 2/3** |

## B3. Seed replicate a2 — equal budget N=1e4, cell C2

gate **FAIL** — `ckpt/d2sx_N10000_a2.pt`, header `NO GATE RECORD mentions d2sx_N10000_a2.pt -- UNVERIFIED here`. Equal budget N=1e4. n=2560. Source `/home/HTJ/t2/conf/results/tables_D2_B1e4s2.txt`.

- TABLE A −3 dB (no test): **V1 0.150 (0.136, 0.164)** — inside a1's 95% CI [0.132, 0.159]. V0 **0.881** (0.868, 0.893). V4 0.154, V4b 0.168. `:58-76`
- bstar → V1, POWERED: −3 317:54 p=2.1e-46 · +0 142:17 p=9.5e-26 · +3 42:8 p=1.2e-06 · **pooled 501:79 p=5.2e-76**; gap **+1.68 dB** [+1.46, +1.94]. `:367-372`
- R2-ours-G → V1: pooled 761:67 p=7e-150, gap +2.17 dB [+1.94, +2.43]. bstar→V4 pooled 483:81 p=1.2e-70. bstar→V4b pooled 452:94 p=4e-57. bstar→V0 pooled 25:5936 p=0. All POWERED. `:337-342, :373-384, :361-366`
- V0→V1 ratio: `1 − 0.150/0.881 = 83.0 %` — **NO TEST EXISTS**.
- **Caveat that must travel:** the seed changes **only the diffusion checkpoint**. `M-ours-bstar`, `M-ours-bstar-scalar`, `M-ours-gmm32`, `R2-ours-G`, `R1-turbo`, `R0-pilot`, `R3-bigamp`, `R4-*`, `R5-genie` rows and the **mandatory control (63:85 / 45:40 / 17:24, pooled 125:149 p=0.16)** are **byte-identical to `tables_D2_B1e4.txt`**. a2 adds **no** seed evidence for the baselines or for the control.

## B4. The mandatory control (10_SPEC §3c): M-ours-bstar → M-ours-bstar-scalar

Both arms are the fitted GMM; **gate not applicable**. Equal budget in every block. n=2560. **POWERED in all four.**

| block | per-point | pooled | SNR@0.1 gap | verdict |
|---|---|---|---|---|
| C2, N=1e4 | 63:85 p=0.084 · 45:40 p=0.66 · 17:24 p=0.35 | **125:149 p=0.16** | +0.04 dB [−0.12, +0.19] | `0/3 each way -> not significant` |
| C2, N=4e4 | 67:86 p=0.15 · 22:43 p=0.013 · 5:25 p=0.00032 | **94:154 p=0.00017** | −0.22 dB [−0.37, −0.09] | `first arm fewer failures at 2/3 -> significant` (**matrix site wins**) |
| C1, N=1e4 | 330:496 · 377:476 · 410:513 | **1117:1485 p=5.7e-13** | n/a (>15 vs >15) | significant 3/3, **matrix site wins** |
| C5, N=1e4 | 202:317 · 194:325 · 192:327 | **588:969 p=3.7e-22** | n/a | significant 3/3, **matrix site wins** |

Sources: `tables_D2_B1e4.txt:385-390`; `tables_D2_B4e4.txt:385-390`; `tables_D2_B1e4x.txt:606-611` and `:746-751`.
**The control is null in exactly one of four blocks.** Quoting only p=0.16 presents it as cleaner than the data.

## B5. Divergence guard (F3), equal-budget runs

`DIVERGE_NMSE = 10.0`, reused from `code/bigamp.py`, not re-chosen. **Detection and classification only — no trajectory was altered.** Aggregates in TABLE A **keep** the diverged blocks.

**C2, N=1e4** (`guard_D2_B1e4.txt:18-27`) — only V0 fires:
−3 1822/2560 = 0.712 (worst 3.322e+07) · +0 2108 = 0.823 (4.573e+08) · +3 2135 = 0.834 (3.966e+09) · +6 2005 = 0.783 (2.619e+09) · +9 1705 = 0.666 (4.177e+09) · +12 1312 = 0.512 (2.143e+09) · +15 927 = 0.362 (7.67e+07).
Never fired (12 arms): M-ours-bstar, M-ours-bstar-scalar, V1, V4, V4b, M-ours-gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp. N/A: R5-genie.

**C2, N=4e4** (`guard_D2_B4e4.txt:18-27`) — V0 only: 0.702 / 0.800 / 0.879 / 0.874 / 0.826 / 0.702 / 0.512. Same 12 arms never fire. **V0's divergence rate is HIGHER at N=4e4 than N=1e4 from +3 through +15 dB even though V0's BLER improves.**

**C2, seed a2** (`guard_D2_B1e4s2.txt:18-27`) — V0 only: 0.821 / 0.859 / 0.809 / 0.769 / 0.637 / 0.479 / 0.340. V0's seed spread in BLER (0.789 → 0.881) tracks its divergence spread (0.712 → 0.821).

**C1 + C5, N=1e4** (`guard_D2_B1e4x.txt:18-78`) [CROSS-CHECKED, X6]:
- C1 V1: −3 **2560/2560 = 1.000** (4.153e+23) · +0 1/2560 = 0.000 · +3 77 = 0.030 · +6 246 = 0.096 · +9 441 = 0.172 · +12 507 = 0.198 · **+15 522 = 0.204** ← the maximum
- C1 V0: 1.000 (2.097e+17), 0.945, 0.957, 0.957, 0.918, 0.891, 0.813
- C1 V4: fires at **−3 dB only**, **2552/2560 = 0.997**, worst 1.815e+28
- C1 V4b: **2560/2560 = 1.000 at all 7 SNRs** (worst 3.9e+17 – 5.2e+17)
- C5 V1: −3 **0** · +0 2 = 0.001 · +3 13 · +6 40 = 0.016 · +9 65 = 0.025 · +12 88 = 0.034 · +15 87 = 0.034
- C5 V0: 0.815 (1.908e+09), 0.866, 0.868, 0.862, 0.830, 0.654, 0.480. C5 V4: never fires. C5 V4b: 1.000 at all 7
- **GMM and classical arms DO fire, at low but non-zero rates:** M-ours-bstar C1 −3/+0/+6/+12 = 2 (0.001, worst 10.67–11.81), C1 +9/+15 = 3 (worst 60.48 / 19.03), C5 +6 = 1, C5 +15 = 2. M-ours-bstar-scalar C1 +9 = 2, +12 = 6 (0.002, worst 1.775e+04), +15 = 5; C5 +6/+9/+12/+15 = 1/1/2/4. M-ours-gmm32 C5 +15 = 1. R3-bigamp C5 +15 = 1.
- Never fired anywhere on D2 (5 arms): R0-pilot, R1-turbo, R2-ours-G, R4-llr, R4-scvamp.

---

# (C) MECHANISM

## C1. Jacobian spectrum — D1 vs D2

**Measurement type: PRIOR-SPACE. No cell, no SNR, no receiver.** n = **48 held-out samples per grid point × 64 eigenvalues**, **4 grid points** (k = 0, 6, 12, 18). **Power: no test exists — no paired test was run on any spectrum quantity.**

**D1, gate PASS** (`ckpt/sx_N160000_D1.pt`: GA 9.879e-16, GB 2.659e-3, GC 9.986e-2, GD 7.183e-2 — **PASS rests on GB/GC/GD; GA is a structural zero**). Equal budget **NO**: learned N=1.6e5 vs the FITTED reference (kron K=32) fitted at N=1e4; the TRUE prior is closed-form and carries no budget.
Source `results/jac_spectrum.txt:92-104` (ADDENDUM 2026-09-21 21:55).

- **n_neg = 0 of 64 at all four grid points, for learned, TRUE and FITTED alike.**
- learned λmin/25%/λmax at σ = .0329/.0899/.2452/.6690: .9407/.9789/1.012 · .6765/.8664/1.073 · .2232/.4702/1.190 · .0308/.1184/1.317
- TRUE: .9450/.9798/1.019 · .6978/.8670/1.096 · .2369/.4699/1.162 · .0403/.1163/1.350
- Relative error vs TRUE (learned / fitted, %) — **λmin** 0.46/2.55 · 3.05/11.22 · 5.78/9.58 · **23.47/2.63** (learned closer 3 of 4; **fitted closer at the largest σ**). **25th percentile** 0.09/0.01 · 0.07/0.05 · 0.06/0.32 · 1.81/0.77 (learned closer 1 of 4; both under 2 %). **λmax** 0.69/3.14 · 2.10/11.22 · 2.41/21.00 · 2.44/4.44 (learned closer **4 of 4**).

**D2, gate NOT VERIFIABLE BY CONSTRUCTION** — D2 has no true score, so GA–GD are D1-only (`04_SPEC §5`). Diagnostic probe on `ckpt/d2sx_N160000_a1.pt` (patience-stopped 1784 epochs, best val 3.519379e-01 @1764, sha256 4443921ce8d5c4a1…). Equal budget **NO**: learned N=1.6e5 vs FITTED kron K=512 at N=1e4 (16×). Source `jac_spectrum.txt:132-138` (ADDENDUM 2026-09-21 23:50).

- learned at σ = .0331/.0920/.2561/.7126 — **n_neg (of 64): 6.71 / 19.79 / 13.50 / 0.69**; n<0.1: 26.52 / 37.58 / 41.10 / 35.50; 25th pct: 0.0381 / **−0.0104** / 0.0063 / 0.0565; λmin: −0.140 / −0.298 / −0.451 / −0.033
- FITTED (kron K=512): **n_neg 0.00 at all four**; n<0.1: 3.44 / 6.54 / 11.19 / 16.94; 25th pct: 0.9476 / 0.6654 / 0.2028 / 0.0916
- **Budget sweep of n_neg:** N=1e4 → 8.0 / 10.6 / 11.2 / 7.8; N=1.6e5 final → 6.71 / 19.79 / 13.50 / 0.69. **Worse at 2 of 4 σ (k=6, k=12), better at k=0 and k=18.** The budget axis is **confounded with stopping epoch** (673 / 1051 / 1784 epochs).
- **f(λmin(Jr) < 0) at k=0**, n=128/point, all 20 grid points: D2 N=1e4 **0.977**, N=4e4 **0.992**, N=1.6e5 **final permanent checkpoint 0.992**. **D1 N=1.6e5: 0.000 at all 20 grid points.**

**Non-conservativity is NOT the discriminator** (`jac_spectrum.txt:172-173`, ADDENDUM 2026-09-22 00:15): D1 asym(Jr) = 1.88e-3 / 1.08e-2 / 3.74e-2 / 8.39e-2 (rising monotonically to 9.8e-2 at σ=0.791) with f(λmin<0) = 0.000 everywhere; the D2 asym row is 1.8e-1 / 2.6e-1 / 2.6e-1 / 1.6e-1. **Same order of magnitude at the top of the grid (~3×), opposite sign outcome.**

**V1's PSD-projection identity margin:** `selftest_M6` asserted the projection is the identity because λmin sits **780×** above `LAM_MIN = 1e-6`. Measured over the full σ grid the fitted GMM's λmin reaches **7.6e-5 at k=12, i.e. 76×**. **Quote 76×, not 780×.** (`jac_spectrum.txt:67-71`.) — but note **the pre-registered test M6 itself has no recorded result** (X13).

## C2. The §6h counterfactual — SIGN vs MAGNITUDE

**n = 256 paired trials per SNR point, 7 SNRs.** D2 / cell **C2** (Tp=4) / −3…+15 dB.
**gate FAIL** — `ckpt/d2sx_N10000_a1.pt`; run meta verbatim: `caller override, NOT verified against the gate record here (recorded PASS rows: none)`. **These are NOT arms and appear in no BLER table.**
**equal budget: YES internally** — every learned row is the same N=1e4 checkpoint; `gmmB|*` rows use the fitted kron K=512 GMM fitted at N=10000.
**power: NO POWER-GUARD VERDICT EXISTS** — this diagnostic never ran through `analysis.py`, so no POWERED/UNDECIDED label was produced. **Do not present it as a powered comparison.**
Source: `/home/HTJ/t2/conf/results/jacpsd_counterfactual_SUMMARY_n256.txt:12-24, :38-51, :54-61`. Raw: `results/diag/jacpsd-counterfactual_D2_C2_snr{-3,+0,+3,+6,+9,+12,+15}_n256.npz`.

**BLER@16** (four decimals as the source carries them; STATUS rounds to three):

| arm\|intervention | −3 | +0 | +3 | +6 | +9 | +12 | +15 |
|---|---|---|---|---|---|---|---|
| `dscore\|eta` (no intervention) | 0.8242 | 0.9023 | 0.8945 | 0.7773 | 0.6641 | 0.5000 | 0.3320 |
| `dscore\|psd1e-2` (**sign repaired**) | 0.1758 | 0.0430 | 0.0117 | 0.0039 | 0.0039 | 0.0000 | 0.0000 |
| `dscore\|abs1e-2` (**\|eig\| floored, SIGN KEPT**) | 0.7930 | 0.8750 | 0.7734 | 0.6133 | 0.4219 | 0.2383 | 0.0977 |
| `dscore\|belsc` (D-14 site removed) | 0.1680 | 0.0391 | 0.0156 | 0.0078 | 0.0000 | 0.0000 | 0.0000 |
| `dscore\|mean` (clip='mean') | 0.1836 | 0.0391 | 0.0039 | 0.0039 | 0.0039 | 0.0000 | 0.0000 |
| `gmmB\|eta` (fitted GMM) | 0.3008 | 0.0898 | 0.0273 | 0.0156 | 0.0000 | 0.0156 | 0.0000 |
| `gmmB\|tiny4` (4 smallest \|eig\| → +1e-4, still PD) | 0.3047 | 0.0898 | 0.0234 | 0.0156 | 0.0000 | 0.0156 | 0.0000 |
| `gmmB\|flip4` (**signs flipped at GMM magnitude**) | **0.4180** | **0.1172** | 0.0273 | 0.0156 | 0.0078 | 0.0156 | 0.0000 |
| `gmmB\|epsite` | 0.3242 | 0.0938 | 0.0195 | 0.0117 | 0.0000 | 0.0156 | 0.0000 |
| `gauss\|sitesc` | 0.3750 | 0.1172 | 0.0273 | 0.0273 | 0.0078 | 0.0117 | 0.0039 |

**Pre-registered prediction, scored** (`:54-61`): `psd1e-2` within 0.02 of `belsc` at **7/7** (gaps +0.008 +0.004 −0.004 −0.004 +0.004 +0.000 +0.000); `abs1e-2` at **0/7** (gaps +0.625 +0.836 +0.758 +0.605 +0.422 +0.238 +0.098); `mean` **7/7**; `eta` **0/7**.
**Disclosure that must travel with the 7/7:** the pre-registration is *before READING*, not *before RUNNING*. The seven `.npz` files were written 2026-09-21 16:23–17:13 KST; the §6h prediction was committed 2026-09-22 12:48 (commit 7ec3d37), the roll-up 13:02 (1badcf0). The data sat unread on disk for ~20 hours. The spec discloses this itself (`10_SPEC_stageC.md:611ff`).
**At n=256 the BLER resolution is 1/256 = 0.0039**, so the 0.02 tolerance is ≈ five trials. Three repairs (`psd1e-2`, `belsc`, `mean`) are indistinguishable within 0.02 of each other.

**Divergence fraction (NMSE@16 > 10)** (`:40-51`): `dscore|eta` 0.172 / 0.223 / 0.199 / 0.184 / 0.090 / 0.070 / 0.016. `dscore|abs1e-2` **0.012 / 0.016 / 0.012 / 0.008 / 0.000 / 0.000 / 0.000** — **not zero**. `psd1e-2`, `belsc`, `mean`, `gmmB|epsite`, `gmmB|eta`, `gmmB|flip4`, `gmmB|tiny4`, `gauss|sitesc`: **0.000 at all seven**.

**Repaired learned prior vs equal-budget fitted GMM** (`psd1e-2` vs `gmmB|eta`, both N=1e4, no paired test, no power verdict): **5 wins / 1 loss / 1 tie** — wins at −3 (0.1758 vs 0.3008), +0 (0.0430 vs 0.0898), +3 (0.0117 vs 0.0273), +6 (0.0039 vs 0.0156), +12 (0.0000 vs 0.0156); **LOSS at +9** (0.0039 vs 0.0000); **TIE at +15** (both 0.0000). Losing and tied margins are **1 block and 0 blocks out of 256**.

## C3. Two-way do() intervention

**n = 64 paired trials per SNR point, 2 SNR points (0 dB, +6 dB)** [CROSS-CHECKED: STATUS.md:312 heads this table "n=128"; the sources say 64 and STATUS's own audit item 7 (`:216`) and the warning at `:330` both say 64. **Use n=64.**]
D2 / cell C2 (Tp=4) / prior S2 / 16 outer iterations / β=0.7.
**gate FAIL** — frozen `ckpt/d2sx_N10000_a1.pt`. Source states verbatim: `NOT A RESULT: d|scorew+psd / +clipmean / +gmmJ are diagnostic probes. Their BLER was seen BEFORE any pre-registration and none of them may enter a table on the strength of these numbers.`
**equal budget: YES internally** — one frozen N=1e4 checkpoint, exactly one factor moved at a time inside frozen wiring (`mode='scalar', scal='belief', hsite='matrix', clip='eta'`); the GMM reference is the exact score of the mixture fitted at N=1e4.
**power: NO VERDICT EXISTS.** Worse: the pre-registered floor (`08_SPEC_analysis.md:42`) needs ≥3 decision points with ≥6 discordant pairs at ≥2 of them. This has **2** decision points, so **if the guard were applied it would read UNDECIDED.** Quote the McNemar p-values only alongside that fact.
Source: `results/diag/h4-jswap_summary.txt:17-31`; `results/diag/jacpsd-counterfactual_SUMMARY.txt` §2.

BLER@16 (±95 %) at **0 dB / +6 dB**: `d|scorew` (= M-ours-dscore) 0.922(.034) / 0.719(.056) · `d|scorew+gmmJ` **0.062(.030) / 0.000(.000)** · `g|scorew` 0.109(.039) / 0.031(.022) · `g|scorew+dJ` **0.953(.026) / 0.922(.034)** · `d|scorew+psd` 0.031(.022) / 0.000 · `d|scorew+clipmean` 0.047(.026) / 0.000 · `gauss|sitesc` anchor 0.078(.034) / 0.016(.016).
Paired McNemar, discordant pairs, one-sided, p < 1e-13 each: `g|scorew → +dJ` **54:0 / 57:0**; `d|scorew → +gmmJ` **0:55 / 0:46**; `d|scorew → +psd` 0:57 / 0:46; `d|scorew → +clipmean` 0:56 / 0:46. **Both directions must be quoted — the reverse direction is what makes the causality two-way.**

**The source's own conclusion is that the single-cause claim is "one factor short":** there are **two independently sufficient repairs** — replace the Jacobian, **or** change the clip rule from `eta` to `mean` — so the collapse is an **interaction** between an indefinite J and `clip='eta'`, not one component.

**Sign vs magnitude, same n=64 file:** `dscore|abs1e-2` (|eig| floored, sign kept) BLER 0.922 / 0.578 — identical at 0 dB to the untouched arm; NMSE_H median 0.5596 / 0.5397; frac NMSE>1 0.375 / 0.281. `gmmB|tiny4` 0.109 / 0.031 — **unchanged**. `gmmB|flip4` (signs of the 4 smallest |eig| flipped, |eig| 33× larger than the diffusion's) **0.141 / 0.016** — a mild degradation that does **not** reproduce the collapse. JFix counter (fraction of J's indefinite before intervention): `psd1e-2` 94.8 % / 98.6 %; `abs1e-2` 69.2 % / 97.0 %.
**Defensible formulation from the source: the sign is the switch, the magnitude sets the gain (damage ~ 1/|eig|).**

## C4. Indefiniteness, not clip firing, is the discriminator

Independent re-check on a **held-out channel stream 11** (not the published stream 10), noise seed 20260921, reference = `score.ExactGMMTorch`, **n = 96 q per ν, 4 ν values**, all in-grid. D2, prior-space / site-level — **no cell, no SNR**. gate FAIL (`d2sx_N10000_a1.pt`). Equal budget YES (learned N=1e4 vs K=512 mixture fitted at N=1e4). **No test exists.**
Source `results/diag/h4-jswap_summary.txt:54-65`; raw `h4-jswap_psd_independent.npz`.

| ν | frac λmin(J)<0 | frac λmax(J)>1 | med #eig<0 | med clip shift | med \|J−J^H\|/\|J\| |
|---|---|---|---|---|---|
| 2.60e-01 diffusion | **0.698** | 0.948 | 1.0 | 1.995e+00 | 1.063e-01 |
| 2.60e-01 ExactGMM | **0.000** | **0.792** | 0.0 | 2.692e-03 | 7.63e-16 |
| 9.32e-02 diffusion | 0.958 | 0.927 | 3.0 | 4.420e+00 | 1.119e-01 |
| 9.32e-02 ExactGMM | 0.000 | 0.667 | 0.0 | 3.979e-04 | 4.51e-16 |
| 3.35e-02 diffusion | 1.000 | 0.979 | 7.0 | 2.349e+00 | 1.071e-01 |
| 3.35e-02 ExactGMM | 0.000 | 0.562 | 0.0 | 2.444e-06 | 3.16e-16 |
| 1.69e-02 diffusion | 0.990 | 0.938 | 6.0 | 3.039e+00 | 1.724e-01 |
| 1.69e-02 ExactGMM | 0.000 | 0.510 | 0.0 | 2.091e-08 | 2.31e-16 |

**This block EXPLICITLY CORRECTS an earlier published claim:** the GMM's J has λmax>1 on **51–79 %** of held-out q, which also drives Λ negative and trips the floor. **"The clip fires for the learned model and not the GMM" is FALSE.** It also corrects the belief-mean shift magnitude: the published 6.96e+03 / 2.88e+03 / 8.70e+02 was measured **along the already-diverged trajectory**; the clean held-out figure is **2.0–4.4** (still 3–6 orders above the GMM's 2.7e-03 – 2.1e-08). Direction survives, magnitude does not.

## C5. Site-level isolation at the receiver's operating ν

**n = 256 held-out samples at ONE grid point, k=6** (σ = 9.2011e-02, ν = 1.6932e-02, chosen because C2's median ν_q at +6 dB is 1.837e-02). D2, σ grid k=6 — tied to C2 at +6 dB **only through the median ν_q match**. gate FAIL. Equal budget YES (both N=1e4). No test exists.
Source: `results/diag/jacobian-psd_split_D2_k6.txt`.

- diffusion: **SigH indefinite 255/256**, shift_med 1.870e+00, shift_p90 5.943e+01, shift_max 1.525e+06, ‖η‖/‖q/ν‖ 2.564, cond(SigH) 4.105e+02; PD-but-λmax(J)>1 1/256 (shift 3.077e-03); PD-and-λmax≤1 **0/256**
- GMM-exact (kron, K=512): **SigH indefinite 0/256**; PD-but-λmax>1 **133/256** (shift_med 3.516e-04, max 9.272e-03); PD-and-λmax≤1 123/256 (shift exactly 0)
- Independent re-derivation, different stream (seed 987654321, **n=128**): diffusion frac λmin(Herm J)<0 = **1.000**, med λmin −6.558e-02, med |λmin| 2.882e-03, med cond 3.909e+02, site shift med 1.857; GMM 0.000, med λmin +9.941e-02, shift 8.969e-10.

**Do not mix n's:** the 20-point companion file `results/diag/jacobian-psd_D2.txt` is a **separate n=64** measurement where the same k=6 row reads f<0(Herm J) = 0.969 and shift_med = 1.813. STATUS.md:278 cites the 255/256 and 1.87 figures under the glob `results/diag/jacobian-psd_*`, which points at the n=64 file where they do not appear. **Correct source is `jacobian-psd_split_D2_k6.txt`.**

## C6. Receiver-side clip fraction and belief-mean shift

Read out of the pre-registered raw `.npz` only (`raw_supp/`), **640 trials per SNR, 7 SNRs**, nothing re-run. D2 / C2 (Tp=4) / −3…+15 dB. gate FAIL (N=1e4, supplementary run `tables_D2_supp.txt`). Equal budget YES (N=1e4). **No test exists — trajectory markers, not a paired comparison.**
Source `results/diag/jacobian-psd_receiver_clip_C2.txt`.

- M-ours-dscore: clip fraction 0.9904 / 0.9979 / 1.0000 / 1.0000 / 1.0000 / 1.0000 / 1.0000; shift mean 4.3e3 → 1.1e5; shift max 5.5e7
- M-ours-bstar: clip fraction 0.44–0.74; shift mean 1.4e-4 – 5.5e-3; max 6.5e-2
- M-ours-gmm32: clip fraction 0.30–0.57; shift mean 7.1e-5 – 3.4e-3; max 3.1e-2

**MARKER, NOT DOSE — this caveat must travel or the number is unusable.** `RouteAClip` records the shift from the **pre-recompute** η regardless of clip mode (`Demo/t2_gmm.py:120` precedes `:121`), so the fully repaired `dscore|mean` records shift **1.146e+03 at 0 dB** — same order as the broken arm — while achieving BLER 0.047. The table's own **12 dB point breaks** the claimed shift↔NMSE correspondence: shift is at its **minimum** there (1.61e3) while BLER is still 0.523.

## C7. The Tp < Nt cavity-variance floor (§6j)

**Closed form** (analysis, carries no gate): `aL = (1 − Tp/Nt) + (Tp/Nt)/(1 + Nt·c̄/σ²)`; `ν_q(iteration 1) = c̄·aL/(1 − aL)`; high-SNR limit `c̄·(Nt − Tp)/Tp`. Limits: **C1 (Tp=2) 1.000 · C5 (Tp=3) 0.3333 · C2 (Tp=4) 0.** Derived from the t=0 data column being x̄=0, so A_n=0 and G becomes pilot-only, leaving Nr(Nt−Tp) null directions (`Demo/t2_route_a.py:301-305`).

**Independent recomputation** (σ² = 10^(−SNR/10), Nt=4, **c̄=1 assumed** — the source does not state c̄ explicitly) vs measured C1 iteration-1 σ_t = √(ν_q/2):

| SNR | predicted ν_q | predicted σ_t | measured σ_t | rel. error |
|---|---|---|---|---|
| −3 dB | 1.997631 | 0.999408 | 0.9993 | 0.011 % |
| +0 dB | 1.500000 | 0.866025 | 0.86585 | 0.020 % |
| +15 dB | 1.015811 | 0.712675 | 0.71246 | 0.030 % |
| high-SNR asymptote | 1.000000 | 0.707107 | — | — |

**Verified at three SNRs, not two** (the +0 dB point is not scored in STATUS and it also hits), all within 0.03 % — far inside the ±5 % band the pre-registration committed to.

**n:** 8 trials per point NOMINAL. **[CROSS-CHECKED, X15] At −3 dB the learned arm's out-of-range denominator is 48 = 3 trials × 16 iterations, not 128 = 8 × 16** — five of the eight trials produced no σ_t record because the learned arm sent νE to infinity and `I/νE + G` went singular (LinAlgError, fixed the same hour). The control arms at the same point have the full 128. **The headline "100 % out of grid" rests on 3 of 8 trials and the file does not say so beside the percentage.**
D2 / cell **C1 (Tp=2)** [**file header mislabels it Tp=4** — X14] / −3, +0, +15 dB. **gate FAIL** — n=8 diagnostic probe on `d2sx_N10000_a1.pt`; **not an arm; appears in no BLER table.** Equal budget YES (all arms N=1e4). **No test exists.** BLER@16 figures here are over 8 trials, resolution 0.125 — **trajectory labels, not BLER results.**
Source: `10_SPEC_stageC.md:705-711` (pre-registered, commit 7737551 at 13:06; result file written 13:09 — a clean pre-registration); `results/diag/sigma-coverage_D2_C1_n8.txt:18-120`.

**Grid coverage.** Frozen trained/gated σ_t range = **[3.306220e-02, 8.451555e-01]**. C1 −3 dB first query 0.9993 = grid top **+18.2 %**. Closed-form sweep across all seven SNRs:

| cell | −3 | +0 | +3 | +6 | +9 | +12 | +15 |
|---|---|---|---|---|---|---|---|
| C1 | **+18.3 %** | **+2.5 %** | −6.4 % | −11.2 % | −13.7 % | −15.0 % | −15.7 % |
| C5 | −16.4 % | … | … | … | … | … | −50.9 % (inside everywhere) |
| C2 | −40.9 % | … | … | … | … | … | −92.6 % (inside everywhere) |

**C1 exceeds the grid top at the two lowest SNRs only.** STATUS §6f states it without the SNR restriction.

**§6j predictions scored** (`sigma-coverage_D2_C1_n8.txt:19-56`): P1 C1 −3 dB σ_t ≈ 0.999 → measured 0.9993 **CORRECT**. P1′ (derived) high-SNR σ_t → 0.707 → +15 dB measured 0.7125 (ν 1.015) **CORRECT**. P2 frac_out_of_grid nonzero at −3 dB, much smaller at +0 → **48/48 = 100.0 %** at −3 dB (all ABOVE the top) and 8/128 = 6.2 % at +0 dB **CORRECT**. P3 the GMM control receiving the same ν_q does not diverge **CORRECT**.
**THE DECISIVE CONTROL, C1 −3 dB iteration 1, same score interface:** `M-ours-dscore` σ_t 0.9993 (top +18 %), NMSE 1.3e11 → 1.5e12 → … → 0.95, BLER@16 1.000. **`ctrl-bstar-sIF` (SAME interface, GMM prior) σ_t 1.046 (top +24 %), NMSE 0.66 → 0.85 → … → 1.02, BLER@16 0.875.** `ctrl-G-sIF` σ_t 0.9993, NMSE 0.66 → 0.71 → … → 0.78, BLER@16 0.750. **The GMM is queried further outside the grid and stays healthy.**

**THE LIMIT OF §6j — must not be dropped** (`:96-111`): C1 **+15 dB**, `M-ours-dscore`: iteration-1 σ_t = **0.7125, INSIDE the grid**, yet iteration-1 NMSE is already **1.974e+02**. Out-of-range fraction 27/128 = 21.1 % and it is entirely **BELOW** the grid bottom. `first it NMSE > 1` = [2 1 2 1 1 1 1 1] — **all eight trials exceed NMSE 1 by iteration 2**; `first it out of range` = [0 5 14 0 0 0 0 3] — **only three of eight ever leave the grid**. ORDER verdict on those 3: `NMSE>1 strictly first 3, same iteration 0, out-of-range first 0`. (At −3 dB: `strictly first 0, same iteration 3, out-of-range first 0`; at +0 dB: `strictly first 0, same iteration 4, out-of-range first 4`.) BLER@16 = 0.750.

**The grid is deliberately NOT widened:** `results/sigma_grid_D2.txt:60` marks it `FROZEN from here on`, and `01_RULES §2` forbids re-running with changed settings after a bad result. **§6j is a measurement, not a repair.**

**V4b as the sharpest confirmation:** V4b uses `scal=site`, so ν_q at t=0 = (1 − Tp/Nt)·1e4 → **C1 5000 / C5 2500 / C2 0**. Measured equal-budget BLER@16 at −3 dB: **C1 0.997 (0.994, 0.998) · C5 0.988 (0.982, 0.991) · C2 0.162 (0.148, 0.176)** — ≈0.99 at every SNR in C1 and C5, with NMSE median 1.27e+17 (C1) / 3.58e+16 (C5) and ok = 0.0725. **The BLER is defined; the channel estimate is garbage.**

## C8. C1 / −3 dB collapse on BOTH testbeds

**D1** (`results/guard_D1_C.txt:18-22`) — **gate-PASSING** N=1.6e5 checkpoint, so **not excusable as a gate-failed artefact**. Equal budget **NO** (learned N=1.6e5, M-ours-bstar N=1e4). n=2560. No test (guard counts).
`M-ours-dscore-C-V0 2560/2560 rate 1.000 worst 4.535e+18` · `V1 2560/2560 worst 1.654e+20` · `V4 2560/2560 worst 1.411e+84` · `V0 C1 +3 dB 11/2560 rate 0.004 worst 3.625e+05`.
Eleven arms never fired anywhere in this raw set: M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32, M-ours-score, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, R6-exactEP. N/A: R5-genie.

**D2 equal budget** (`guard_D2_B1e4x.txt`, gate FAIL, N=1e4): V0 2560/2560 worst 2.097e+17 · V1 2560/2560 worst 4.153e+23 · **V4 2552/2560 = 0.997** worst 1.815e+28 · V4b 2560/2560 worst 4.734e+17 · **M-ours-bstar 2/2560 = 0.001 worst 11.12**.

---

# (D) BASELINES AND GATES

## D1. GMM b* selection rule and fits

**Selection rule, verbatim:** `VALIDATION log-likelihood only. BLER is never consulted (01_RULES §5)`. `gmm_fit_D2.txt:13`, identically `gmm_fit_D2_n4e4.txt:13`. n_val = n_test = 5000 for every K, 3 restarts per configuration. **gate not applicable · equal budget not applicable · no test exists.**

**Nr=8 × Nt=4 kron ll_val, recomputed by me from the `.npz` files** (agrees with the authored summaries to printed precision):

| K | N=1e4 | N=4e4 | N=1.6e5 |
|---|---|---|---|
| 16 | −39.5744 | −38.9906 | −39.0175 |
| 32 | −33.5556 | −33.0224 | −33.0229 |
| 64 | −29.0145 | −27.6826 | −27.4754 |
| 128 | −26.1159 | −23.4998 | **MISSING** |
| 256 | −23.9360 | −19.6991 | −18.4166 |
| 512 | **−23.4734 (b\*)** | **−17.3438 (b\*, EDGE)** | **−14.6361 (best avail., EDGE)** |
| 1024 | **−23.5726 (turns DOWN)** | not fitted | not fitted |
| **last increment K256→K512** | **+0.4626** | **+2.3553** | **+3.7805** |

Sources: `results/gmm_fit_D2.txt:66`; `results/gmm_fit_D2_n4e4.txt:66`; `results/gmm_fits_D2_n16e4/*.npz` (**my own computation — no authored summary file `gmm_fit_D2_n16e4.txt` exists**); `results/gmm_fits_D2_K1024/fit_S2_Nr8_kronK1024_n10000.npz`.

- **N=1.6e5 Nr=8 full family** (complete, K=16…512): −38.1519 / −31.4597 / −25.3440 / −20.2058 / −16.5517 / **−16.3159** — worse than kron at K=512.
- **N=1e4 turnover margin = 0.0992 nat** on one 5000-sample validation set, **no error bar**. Restart scatter at the same K is larger: K=1024 `cand_ll_val = [−23.8329, −24.0051, −23.5726]` (range 0.4325); K=512 range 0.5925.
- **K=1024 fit diagnostics** (`fit_S2_Nr8_kronK1024_n10000.npz`): selected restart **n_reseed = 9144** [X10], ll_train −12.5262, train–val gap 11.046 (vs K=512's 9.134), π_min 9.809e-05, 327 of 1024 components with π < 1e-4, 26 EM iterations, best at 20, 308 s on one GPU.
- **Nr=4, N=1e4:** b* = kron K=512 **on the grid EDGE** (K128 −24.709 → K256 −24.207 → K512 −24.133, increments +0.502 then +0.074). **No K=1024 fit exists for Nr=4 at any budget.** Cells C3/C4 use this fit. (`gmm_fit_D2.txt:30`)
- **Nr=4, N=4e4:** b* = **full K=128, INTERIOR** (−23.038 / **−21.765** / −21.869 / −23.563). The one clean b* in the set; it does not transfer to Nr=8. (`gmm_fit_D2_n4e4.txt:30`)
- **What the mixture buys over the Gaussian sample-covariance prior** (n_test=5000, equal budget N=1e4, no test): N=1e4 Nr=8 kron K=512 **G = ll_test(GMM) − ll_test(Gaussian) = 42.482 nat/sample** (−23.144 vs −65.627); Nr=4 kron K=512 G = 9.779 nat; D1 Nr=8 kron K=64 G = 9.188 nat. (`gmm_fit_D2.txt:78-90`) The file states that absolute log-likelihoods of two different distributions are not comparable, which is why G is the comparable quantity; **no KL column for D2 — D2 has no closed-form true density.**

**Which GMM fit feeds which BLER table** (from each table's own per-arm budget block, `:33-42`):

| table | GMM N_train | learned N_train | equal? | learned gate |
|---|---|---|---|---|
| `tables_D2_B1e4.txt` (C2) | 10000 | 10000 | **YES** | FAIL (D1 twin GC 0.243) |
| `tables_D2_B1e4x.txt` (C1+C5) | 10000 | 10000 | **YES** | FAIL |
| `tables_D2_B1e4s2.txt` (C2, seed a2) | 10000 | 10000 | **YES** | FAIL |
| `tables_D2_B4e4.txt` (C2) | 40000 | 40000 | **YES** | FAIL (D1 twin GC 0.167) |
| `tables_D2_C.txt` (C1+C2+C5) | **10000** | **160000** | **NO — 16×** | sibling-qualified PASS |

**There is exactly one table that is both gate-qualified and C2-covering (`tables_D2_C.txt`), and it is NOT equal budget. There is no table that is both.**

## D2. Pre-registered gates GA–GD

**Definition** (`04_SPEC_diffusion.md:93-98`, restated `10_SPEC_stageC.md:124`): GA (Tweedie self-consistency) ≤ 1e-6 · GB (denoising NMSE excess over the exact score, all σ) ≤ 0.05 · GC (relative score error) ≤ 0.15 · GD (relative Frobenius error of the Wirtinger Jacobian D-14 uses) ≤ 0.20. **PASS = all four.** Evaluated at **n_eval = 512** held-out samples (`common.train_rng` stream 10), **n_jac = 64**, over a frozen 20-point σ grid. **D1 ONLY** — D2 has no closed-form true score (`05_SPEC_testbed_D2.md:47`).
**GD was redefined** on 2026-09-20 12:35, before any checkpoint was gated (`DECISIONS.md`); the old quantity is still printed as `GD_trace` and is **not** the gate (consistently 3–5× smaller).

**GA is a structural zero.** Measured GA: 9.879e-16 (V0), 9.712e-16 (V2), 1.11803e-15 (V3), 1.01071e-15 (L9 a3) — float64 round-off against a 1e-6 threshold. `gate_D1_C.txt:19-21` and `gate_D1.txt:19-21` banners: *GA is identically zero by construction for this model family; it guards score-path vs x0-path inconsistency only, and PASS therefore rests on GB/GC/GD.* **Both facts must travel: the registered rule is four gates; the informative content is three.**
**Source-vs-source:** `samplecx_D1.txt:29` annotates the N=160,000 row `<- clears all four gates`. `gate_D1_C.txt:20` and `LADDER_C.md:1` say PASS rests on GB/GC/GD. **The gate-record files are authoritative for gate values.**

**Sample-complexity ladder** (`results/samplecx_D1.txt:26-30`, D1, n_eval=512, n_jac=64, stream 10, epochs 357/200/200/200):

| N_train | GB (≤0.05) | GC (≤0.15) | GD (≤0.20) | gate_score | verdict |
|---|---|---|---|---|---|
| 2,500 | 0.05523 | 0.78537 | 0.32425 | 5.2358 | FAIL |
| **10,000** | 0.01174 | **0.24333** | 0.16081 | 1.6222 | **FAIL** |
| **40,000** | 0.00453 | **0.16651** | 0.10099 | 1.1101 | **FAIL** |
| **160,000** | 0.00266 | **0.09986** | 0.07183 | 0.6657 | **PASS** |

**At N=1e4, GB and GD are already met; GC alone fails, by a factor of 1.62.** Scaling: `GC ~ N^(−0.474)`, R² = 0.9342, extrapolated 0.15 crossing at N ≈ 52,731, **bracketed by the measured points 4e4 (FAIL) and 1.6e5 (PASS)** (`samplecx_D1.txt:32-35`). Four points, **no CI on the exponent** — the bracketing statement is the defensible one.
**Banner on the file:** `CIRCULAR TESTBED -- true prior is defined as a grid GMM; the GMM arm is correctly specified. No claim about learned priors can be made from this table.`

**TWO GC values circulate for the same "gate-failed N=1e4 checkpoint" caveat, and both are real:**
- **0.24333** — `samplecx_D1.txt:28` / `samplecx.csv`, the D1 sample-complexity ladder at the **registered** N_train=10,000 budget, 200 epochs, val 7.281741e-01, GA 1.089936e-15, GB 1.173690e-02, GD 1.608083e-01, gate_score 1.622225. Quoted by `jacpsd_counterfactual_SUMMARY_n256.txt`, STATUS.md:82/:262/:825, `10_SPEC_stageC.md:453`.
- **0.224111** — `results/hpo_final_r2.txt`, HPO trial 386 retrained at the full ladder budget and re-gated on stream 10: GA 1.03540e-15, GB 7.71573e-03, GC 2.24111e-01 **FAIL**, GD 1.49894e-01 **PASS**, GD_trace 2.96603e-02 reported not gated, gate_score 1.4941, val 7.276164e-01. Quoted by `figs/F8`, `figs/F9`, `settling_D2.txt`, and the `gate_D2.txt` banner copied into five D2 tables.

Both FAIL, so the verdict is unaffected — **but the citation must name which record it is quoting.**

**The only PASS in the project.** `LADDER_C.md:1` (2026-09-21 14:12 KST): SX160000 attempt a1, `ckpt/sx_N160000_D1.pt`, `dit vp/angle w64 d6 lr 2.238046e-3 ema 0.999`: **GA 9.879e-16 / GB +0.27 % / GC 0.0999 / GD 0.0718 → PASS**; GD_trace 0.007462 reported not gated. n_eval=512, n_jac=64, N_train=160000, D1 8×4 prior S.
**TRACEABILITY GAP:** this PASS lives **only** in the append-only `LADDER_C.md` log line. `results/gate_D1_C.txt` was regenerated with the filter `ckpt=ckpt/sx_V3_N160000_D1_a3.pt` (`:10`) and now holds **only the V3 FAIL row**. `results/gate_D1.txt` holds only Stage A/B rows, all FAIL. **STATUS cites `gate_D1_C.txt` for the V0 PASS and the V2 FAIL — those rows are no longer in that file. Cite `LADDER_C.md:1` (V0) and `LADDER_C.md:9` (V2).**

**Stage A/B ladder: 49 gated rows, ZERO PASS.** Best: L9 attempt 3 (`uvit vp/pixel w64 d7`) GA 1.011e-15 / GB +2.89 % / GC 0.3164 / GD 0.2405 → FAIL. HPO best gate_score **1.347** (trial 346, `dit vp/angle w64 d6`: GB 0.01231 / GC 0.2021 / GD 0.163); ladder's own best gate_score 2.109 (L4 a1). `gate_score < 1.0` would mean all four pass. Sources `LADDER.md:73-92`, `gate_D1.txt:27-35`, `hpo_D1.txt:20-26`.
**This is why `M-ours-dscore` is BLOCKED in the pre-registered table on both testbeds: the registered comparison is at N=1e4 and it fails there. The Stage C PASS is at 16× that budget and does not lift the block.**

**Architecture search.** `hpo_D1.txt:14,16,20`: **724 trials total, 724 completed, 0 failed/infeasible**; objective = the pre-registered gate score `max_g G[g]/tol[g]`, **MINIMISED, never BLER (01_RULES §5)**; search on held-out stream 11 at n_eval=256/n_jac=24, reported gates on stream 10; winner retrained at full ladder budget and re-gated. `hpo_strat_D1.txt:9-11,18`: equal-n controlled comparison, first 30 trials per architecture (adm 30, conv 30, dit 30, mlp 32, unet 30, uvit 44 = 196); at equal trials **five of six families are statistically indistinguishable** (unet 1.572 / uvit 1.814 / dit 1.865 / adm 1.872 / conv 1.902; only mlp 4.540 clearly worse). Equal budget: every trial used the identical N_train=1e4 samples. **No power guard applies to the HPO study.**
**[X9] "959 configurations" is NOT reconstructible from the files.** Quote **724 with `hpo_D1.txt`**, or say "over 900 configurations across two searches" and cite both `hpo_D1.txt` and `hpo_strat_D1.txt`.

**No D2 checkpoint has a gate record.** Every D2 table prints, per learned arm: `NO GATE RECORD mentions d2sx_N{10000,40000,160000}_a{1,2}.pt -- UNVERIFIED here. (GA-GD are measurable on D1 only, 10_SPEC §5: a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)` and `dscore_status: ABSENT -- no GATE-PASSING checkpoint ... recorded PASS rows: none`. The qualifying sibling for N=1.6e5 is `ckpt/sx_N160000_D1.pt` (LADDER_C.md:1 PASS); same recipe (`dit vp/angle w64 d6 h8 p1 emb256 lr 2.238046e-3 ema 0.999 batch 256`), same N′=1.6e5, same stopping rule, only the testbed differs. **The sibling argument is a recipe-equivalence inference, not a measurement, and the tables themselves decline to certify it.**
**STATUS.md:825 and `10_SPEC_stageC.md:453` both write "ckpt/d2sx_N10000_a1.pt failed the pre-registered gate (GC 0.243)" as if measured on that file. It was not.**

## D3. Failed variants V2 and V3 (no BLER anywhere)

**V2 (energy parameterisation, s = −∇ₓE_θ).** `ckpt/sx_V2_N160000_D1_a3.pt`, n_eval=512, n_jac=64, N_train=160000, D1: **GA 9.712e-16 PASS / GB 4.542e-03 PASS / GC 1.674e-01 FAIL (11.6 % over 0.15) / GD 8.143e-02 PASS**; GD_trace 0.01595 reported not gated. Equal budget YES vs V0 (both N=1.6e5, same arch/width/depth/ema/batch/emb per §3b). **No test exists — V2 has no BLER row anywhere.** `LADDER_C.md:9`.
**Ladder exhausted:** D2 a1 stopped by DIVERGE_TRAIN at epoch 90 (best val 3.653966e-01 @85); D2 a2 (clip 1.0) best val 3.569986e-01 @85, val then 6.442181e+00 (ep86) → 6.351075e+03 (ep87) → **NaN from ep88 for 103 consecutive epochs** — the guard did not fire because `vl > 3.0*best` is False when vl is NaN (a real §3d implementation bug, found by the 18:20 audit and fixed the same hour to `bad = (vl != vl) or (vl > MULT*best)`); D1 a1 DIVERGE_TRAIN at epoch 54 (val 3.94e+04); D1 a2 DIVERGE_TRAIN at epoch 34 (train loss 8.27e+10). `LADDER_C.md:2,4,5,6`.
**CONFOUND, stated in the source:** V2's D1 twin was finally trained under the §3d fallback at **lr/3 (7.46e-4 vs V0's 2.238e-3)**. No V2 D1 run at the frozen lr ever completed, and the 3-attempt ladder is exhausted. **The GC failure cannot be attributed to the parameterisation rather than the reduced lr.**
**Training-loss observation only:** V2 D2 a3 best val **3.361999e-01 @ epoch 1262** (1282 ep, patience stop, 60892 s, 47.50 s/ep) vs V0 D2 best **3.519379e-01 @ epoch 1764** — **4.5 % lower**. gate: **UNGATED** (D2), twin FAILED. Equal budget YES. **No test — single runs, no seeds, no CI.** `LADDER_C.md:13`.
**DSM validation loss does not predict GC:** D1 val V0 7.398444e-01 vs V2 7.398676e-01 = **0.003 % apart**, while GC is 9.986e-02 vs 1.674e-01 = **68 % higher** (ratio 1.676). Two checkpoints, no repeats. `STATUS.md:620-625`, gate values `LADDER_C.md:1,9`.

**V3 (Jacobian asymmetry penalty, λ = 1.0).** `ckpt/sx_V3_N160000_D1_a3.pt`, n_eval=512 (stream 10), n_jac=64, 20 σ points, N_train=160000, D1: **GA 1.11803e-15 PASS / GB 5.91351e-02 FAIL / GC 3.52507e-01 FAIL / GD 3.44911e-01 FAIL**; GD_trace 1.45260e-01 reported not gated; best val 7.488075e-01 @159. VERDICT FAIL — **three gates**. Equal budget YES vs V0; λ fixed at 1.0 and never tuned (tuning would violate A2). **No test exists.** `results/gate_D1_C.txt:27-35` (per-σ table `:38-58`); `LADDER_C.md:12`.
**The regulariser made its own target worse:** GD 7.183e-02 → 3.449e-01 = **4.80×**; GC 9.986e-02 → 3.525e-01 = **3.53×**. GD rises from 5.907e-03 at k=0 to 3.449e-01 at k=19. The stated mechanism (the model stopped fitting the score at all) is **inferred from the two gate values, not separately measured.**
**Same lr confound** (attempts 1 and 2 diverged; attempt 3 used clip 1.0 + lr/3). **λ sweep incomplete:** λ=0.1 attempt 1 diverged at epoch 100, best val 7.456974e-01 @44 (below V0's 7.398); λ=1.0 D2 a1 DIVERGE_TRAIN at epoch 35 (ran to 62), best val 6.919234e-01 @27; λ=1.0 D1 a1 and a2 both diverged. `LADDER_L0.1.md`; `LADDER_C.md:3,10,11`.

**Neither V2 nor V3 appears as an arm in any BLER table, on either testbed, at any budget.** Every D2 table's arm list contains V0, V1, V4, V4b, M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32, R0/R1/R2/R3/R4-llr/R4-scvamp/R5-genie — and no V2 or V3. `M-ours-dscore` is listed ABSENT/BLOCKED in all five (`tables_D2_C.txt:21-24, :43`).

## D4. Frozen Stage A/B classical results (`results/tables_D2.txt`)

**n IS NOT 2560 at all decision points in this file.** Cell C2 `n per SNR: [2560, 2560, 640, 640, 640, 640, 640]` (`:189`) [X11]. **gate not applicable** (all arms classical). All POWERED unless stated.

| pair | cell | decision SNRs (n) | counts / p | pooled | SNR@0.1 gap | equal budget | source |
|---|---|---|---|---|---|---|---|
| R1-turbo → R2-ours-G | C2 | +0 (2560) / +3 (640) / +6 (640) | 291:1 p=7.4e-86 · 32:0 p=4.7e-10 · 11:1 p=0.0063 | 334:2 p=8.1e-97 | **+2.77 dB** [+2.13, +3.42] | YES, N=1e4 | `:771-777` |
| **R2-ours-G → M-ours-bstar** | C2 | −3 (2560) / +0 (2560) / +3 (**640**) | 274:79 p=2.5e-26 · 86:44 p=0.00029 · 14:3 p=0.013 | 374:126 p=1.4e-29, sig 3/3 | **+0.49 dB** [+0.30, +0.72] | YES, N=1e4 | `:784-789` |
| R2-ours-G → R4-scvamp | C2 | −3 / +0 / +3 (640) | 5:733 p=2.5e-210 · 5:521 p=3e-147 · 1:81 p=3.4e-23 | 11:1335 **p prints as 0 (underflow) — write p < 1e-300** | **−5.61 dB** [−6.76, −4.81] | YES, N=1e4 | `:790-795` |
| R4-llr → R4-scvamp | C2 | +9/+12/+15 (640 each) | 141:8 p=1.5e-32 · 102:9 p=4.3e-21 · 92:2 p=4.5e-25 | 335:19 **p=7.8e-76** | ≥ +9.40 dB (R4-llr never reaches 0.1) | YES, N=1e4 | `:796-801` |
| R4-llr → R4-scvamp | **C1** | +3 only (640) | 68:19 p=1.2e-07 | — | — | YES, N=1e4 | `:746-751` — **UNDECIDED**, 1 decision point |
| R2-ours-G → R3-bigamp | C2 | −3 / +0 / +3 (640) | 59:609 p=4.3e-116 · 30:314 p=7.9e-61 · 3:33 p=2.3e-07 | 92:956 p=7.2e-182 | **−2.66 dB** [−3.37, −2.06] | **NO** — R2-ours-G N=1e4, **R3-bigamp N_train=0** (i.i.d. CN(0,1/Nr) prior, fits nothing) | `:802-807` |

R3-bigamp's budget is recorded as a **STRUCTURAL** limitation (`correlated prior not supported by Table III`), not budget starvation imposed by us.

**Uniform-n = 2560 replacements exist** in `tables_D2_B1e4.txt`: R1-turbo → R2-ours-G **+2.29 dB** [+1.95, +2.64], pooled 442:4 p=1.8e-125 (`:283-288`); R2-ours-G → M-ours-bstar **+0.49 dB** [+0.31, +0.69], pooled 405:133 p=6.1e-33 with +3 dB 45:10 p=2.1e-06 (`:295-300`). **Prefer these if a uniform n=2560 is wanted.**

**Tp trend of the structured-prior gain** (`results/tp_trend_D2.txt`; **this file uses exact binomial tests at every SNR, not the 3-decision-point guard, so the pre-registered POWERED/UNDECIDED verdicts do not apply**; equal budget N=1e4; gate n/a): R2-ours-G → M-ours-bstar pooled — **C1 (Tp=2) 1256:1157 p=4.6e-02 · C5 (Tp=3) 442:359 p=3.7e-03 but +15 dB 36:64 p=6.6e-03 with the Gaussian ahead · C2 (Tp=4) 392:131 p=3.1e-31 · C3 (4×4, Tp=2) 269:392 p=2.0e-06 with the GAUSSIAN ahead · C4 (4×4, Tp=4) 47:5 p=1.3e-09**. The file states cells are **not** pooled with each other.

## D5. D1 confirmatory results (instrument testbed)

**`CIRCULAR TESTBED` banner on `tables_D1_C.txt:55`, `samplecx_D1.txt:21`, `gate_D1_C.txt:14`: "true prior is defined as a grid GMM; the GMM arm is correctly specified. No claim about learned priors can be made from this table."** D1's true prior = `t2_gmm.angle_grid_prior(S, 8, 4, rho_c=0.7, KG=32)`, a 32×32 = 1024-component grid mixture.

**D1 C1, n=640** (`tables_D1.txt:880-897`, decision SNRs +0/+3/+6, POWERED, gate n/a, equal budget YES for bstar/gmm32 at N=1e4 — M-ours-score and R6-exactEP use the exact prior):
- M-ours-bstar → R6-exactEP: 17:11 p=0.34 · 15:13 p=0.85 · 6:4 p=0.75; pooled 38:28 p=0.27; gap +0.12 dB [−0.20, +0.46] — **not significant**
- M-ours-score → R6-exactEP: 18:33 p=0.049 · 16:21 p=0.51 · 10:6 p=0.45; pooled 44:60 p=0.14; gap −0.07 dB [−0.55, +0.39] — **not significant**
- M-ours-gmm32 → R6-exactEP: pooled 139:66 p=3.8e-07, +3.49 dB [+1.56, +6.05] — **significant**

**Eleven UNDECIDED pairs in `tables_D1_C.txt`, ALL in cell C2, all at n=2560, all anchored at only 2 decision SNRs (−3/+0) because the anchor leaves the BLER window [0.005, 0.9] from +3 dB up:**

| pair | per-point | pooled | discordant counts | gate | equal budget | line |
|---|---|---|---|---|---|---|
| M-ours-gmm32 → R6-exactEP | 87:61 p=0.04 · 38:18 p=0.01 | 125:79 p=0.0016 | [148, 56] | n/a | YES N=1e4 | `:937-942` |
| M-ours-bstar → R6-exactEP | 38:25 p=0.13 · 15:11 p=0.56 | 53:36 p=0.089 | [63, 26] | n/a | YES N=1e4 | `:943-948` |
| M-ours-score → R6-exactEP | 10:6 p=0.45 · 6:7 p=1 | 16:13 p=0.71 | [16, 13] | n/a | n/a (both exact prior) | `:949-954` |
| M-ours-bstar → V0 | 47:44 p=0.83 · 18:18 p=1 | 65:62 p=0.86 | [91, 36] | **PASS** (sx_N160000_D1.pt) | **NO** — 1.6e5 vs 1e4 | `:979-984` |
| M-ours-bstar → V1 | 47:44 · 18:18 | 65:62 p=0.86 | [91, 36] | PASS | NO | `:985-990` |
| M-ours-bstar → V4 | 61:91 p=0.018 · 25:33 p=0.36 | 86:124 p=0.011 | [152, 58] | PASS | NO | `:991-996` |
| M-ours-bstar → M-ours-bstar-scalar | 57:92 p=0.0052 · 20:28 p=0.31 | 77:120 p=0.0027 | [149, 48] | n/a | YES N=1e4 | `:997-1002` |
| V0 → R6-exactEP | 41:31 p=0.29 · 15:11 p=0.56 | 56:42 p=0.19 | [72, 26] | PASS | n/a | `:1003-1008` |
| V1 → R6-exactEP | 41:31 · 15:11 | 56:42 p=0.19 | [72, 26] | PASS | n/a | `:1009-1014` |
| V4 → R6-exactEP | 88:45 p=0.00024 · 32:20 p=0.13 | 120:65 p=6.4e-05 | [133, 52] | PASS | n/a | `:1015-1020` |
| M-ours-bstar-scalar → R6-exactEP | 94:46 p=6.1e-05 · 26:14 p=0.081 | 120:60 p=9.1e-06 | [140, 40] | n/a | n/a | `:1021-1026` |

V0 and V1 print **byte-identical** counts on D1 because the PSD projection never fires there — that identity is evidence about D1's Jacobian, **not a second independent result**.
**The only POWERED "ties the exact-EP bound" statement on D1 is C5: V0 → R6-exactEP 88:91 p=0.88.**
**On D1, `M-ours-bstar-scalar` (scalarisation hurts the GMM) is POWERED and significant on C1 (268:443 p=5.5e-11, 3/3) and C5 (129:270 p=1.4e-12, 2/3) but UNDECIDED on C2.**

## D6. Power-guard census

| file | pairs | UNDECIDED | which | source |
|---|---|---|---|---|
| `tables_D1_C.txt` | — | **11** | all C2, all at 2 decision points | `:937-1026` |
| `tables_D2_C.txt` | — | **8** | the 7 arm→R5-genie pairs on C2 + R4-llr→R4-scvamp on C1 | `:746-751, :898-999` |
| `tables_D2_B1e4.txt` | 23 | **7** | gmm32 / bstar / V0 / V1 / V4 / V4b / bstar-scalar each → R5-genie | `:391-414` |
| `tables_D2_B4e4.txt` | 23 | **7** | same seven | `:391-414` |
| `tables_D2_B1e4s2.txt` | 23 | **7** | same seven | `:391-414` |
| `tables_D2_B1e4x.txt` | 46 (23/cell) | **1** | C1 R4-llr → R4-scvamp (1 decision point) | `:528-533` |
| **TOTAL on record** | | **34 pair-level UNDECIDED verdicts** | | |

**Why the C2 genie pairs are UNDECIDED:** R5-genie is the anchor and sits at or below 0.005 from +3 dB up on C2, so only **two** in-window decision SNRs exist (−3, +0) where **three** are required. Examples — V1 → R5-genie, equal budget N=1e4: −3 dB 294:9 p=6.7e-75 · +0 dB 73:4 p=1.9e-17 · pooled 367:13 p=3.8e-91; guard `2 decision points (needs 3), discordant-pair counts [303, 77]` → **UNDECIDED** (`tables_D2_B1e4.txt:397-402`). At N=1.6e5: −3 299:15 p=9.8e-70 · +0 65:3 p=3.6e-16 · pooled 364:18 p=6.7e-85, counts [314, 68] → UNDECIDED (`tables_D2_C.txt:976-981`). At N=4e4: pooled 357:15 p=4.5e-86, counts [309, 63]. Seed a2: pooled 373:15 p=1.3e-90, counts [320, 68]. **V0 → R5-genie on C2 at N=1.6e5: p = 0 in both cells and still UNDECIDED** (`:970-975`).
**On C1 and C5 the genie pairs ARE powered** — genie stays inside the anchor window there. The C2 restriction does not carry over and vice versa.
**Most extreme case in the record: C1 R4-llr → R4-scvamp, p = 4.3e-36, UNDECIDED and unusable** (1 decision point).

## D7. Implementation-identity tests

`results/tests.txt`: **35/35 PASS** (S4 N/A; S5, S7, T2b, T2c, T2e RECORD). gate n/a · no test statistic · equal budget by construction.
- **M2 = 0.000e+00**, criterion "exactly 0", PASS — routing Module H to a Gaussian reproduces `R2-ours-G` **bitwise** (`:35`)
- M2b = 1.283e-13 (K=1 mixture-EP site reduces to the Gaussian arm; threshold 1e-10) (`:36`)
- M1 = 0.000e+00 (assembler `M-ours-gmm32` == `Demo/exp_0925 'Hgmm-K32'`) (`:33`); M3 = 4.283e-16 (`:37`)
- **T2d PASS**: worst 99.9 % CI upper bound minus the Gaussian value 2 = **−0.2518** (n = 8 angle sets × 20000 phase draws). **T2dm PASS**: max |measured − analytic (2 − Σpₗ²)| = 5.010e-03 (`testbed_D2.txt:17-18`)
- **T2c RECORD**: NMSE_inf(Tp=2) with the DFT pilots in use = **0.466271** vs 1 − Tp/Nt = **0.5000**, |gap| = 0.0337, judged against `T2C_VACUOUS_GAP = 0.05` — and the file states this constant is **`a conf-side constant, not present in 05_SPEC`** (`tests.txt:50`, `testbed_D2.txt:16`)
- **T2e / pilot decision, knife edge**: erank(Rt) = 3.8770/4 = **0.969**; erank(Rr) = 7.3500/8 = 0.919; erank(C_ens) = 28.4958/32 = **0.890**; threshold 0.9; Rt eigenvalues [1.2103, 1.0857, 0.9776, 0.7264]. File verbatim: *`The full-covariance reading (erank(C_ens) = 28.4958 < 0.9*32 = 28.8000) would have said eigen-aligned (informative) -- IT DIFFERS from the decision in force. Knife edge: Rt is 0.969 of full and C_ens is 0.890, on opposite sides of 0.9.`* The decision was taken on Rt because pilots span the transmit side. (`testbed_D2.txt:15`)
- **MISSING: test M6.** `10_SPEC_stageC.md:194` registers M6 — V1's PSD projection must be the IDENTITY on GMM arms, "그 항등성을 신규 시험 M6 으로 검증하고, **실패하면 V1 을 폐기한다**". **M6 appears in neither `results/tests.txt` nor `results/tests_VREV.txt`** (both report 35/35 with identical N/A and RECORD lists). [X13] **The integrity check that guards the V1 arm has no recorded result.**

---

# (E) SCOPE LIMITS AND RETRACTIONS

## E1. The structural limitation

**There is no table that is both gate-qualified AND equal-budget.**
- Equal-budget evidence (B1e4, B1e4x, B1e4s2, B4e4) is **all on gate-FAILED checkpoints** (D1 twin GC 0.243 at N=1e4, 0.167 at N=4e4). §6d/§6f re-registered these as **budget-axis and cell-generalisation MEASUREMENTS, not arm results** — a documented carve-out from `10_SPEC_stageC.md:132-136` (§5b), which says that if the gate fails Stage C ends there and **no BLER is run**.
- Gate-qualified evidence (`tables_D2_C.txt`) is **16× asymmetric**: learned N_train=160000 vs GMM/Gaussian N_train=10000. `01_RULES.md:75`: *"do not give diffusion more data or budget than the GMM (same N_train = 10⁴, same split)"*. `DECISIONS.md` 2026-09-22 01:00 records an explicit reversal of the earlier decision not to publish this head-to-head; the compromise was **"print it with budgets beside it, do not use it as a claim."** Table header verbatim: *"The GMM arms and the learned arms are only equal-budget when their N_train below are EQUAL; read the numbers, not the arm names."*
- **There is no cell × budget grid.** The budget axis (1e4, 4e4) exists **only on C2**; the cell axis (C1, C5) exists **only at N=1e4**.

## E2. Under-fitted GMM baseline — 01_RULES:76

| budget (Nr=8) | b* | interior? | last increment | K=1024 |
|---|---|---|---|---|
| N=1e4 | kron K=512 | **YES** (K=1024 turns down by 0.099 nat) | +0.4626 | fitted, loses |
| N=4e4 | kron K=512 | **NO — grid EDGE** | **+2.3553** | **not fitted** |
| N=1.6e5 | kron K=512 | **NO — grid EDGE** | **+3.7805** | **not fitted** |
| Nr=4, any budget | kron K=512 (N=1e4) | **NO — edge**, increment +0.074 | | **never fitted** |

`DECISIONS.md` 2026-09-22 13:55, in the project's own words: at the larger budgets b*=K=512 sits at the boundary with likelihood rising steeply, K=1024 is likely to win, and therefore `tables_D2_B4e4.txt` (and the forthcoming B16e4) have a baseline that is **UNFAIRLY WEAK — an 01_RULES:76 violation.** `code/fit_k1024_big.sh` states the K256→K512 gain as +0.46 / +2.36 / +3.78 by budget and predicts K=1024 will win at the larger budgets. The B4e4 table carries **no such warning in its header**.
Also: `05_SPEC_testbed_D2.md:56` pre-registers the GMM K grid as K ∈ {16, 32, 64, 128}; the fits actually run K ∈ {16, 32, 64, 128, 256, 512} and (§6l) 1024. **The extension strengthens the baseline and is in our favour, but the spec text and the executed grid differ.**

## E3. No V0 → V1 paired sign test exists anywhere

`code/analysis.py:371-397` `pair_list` builds: `(R1-turbo, R2-ours-G)`, `(REF, M-ours-gmm32/bstar/dscore)`, `(M-ours-bstar, M-ours-dscore)`, [D1 only: `(REF, M-ours-score)`], `(REF, R4-scvamp)`, `(R4-llr, R4-scvamp)`, `(REF, R3-bigamp)`, `(each M_ARM, top)`, then for each of `STAGEC_ARMS = (V0, V1, V4, V4b)`: `(REF, arm)`, `(M-ours-bstar, arm)`, `(arm, top)`. `REF = 'R2-ours-G'` (`:97`); `top = 'R5-genie'` on D2. **No Stage-C-to-Stage-C pair is ever formed.** A grep for `C-V0 -> M-ours-dscore` across `conf/results/*.txt` returns nothing.
**Consequence: the 75.5 % (N=1.6e5), 81.6 % / 80.4 % / 83.0 % (equal budget) and "80.1 % of the gap to genie" figures are ALL TABLE A point-estimate ratios with no p-value, no discordant-pair count and no power-guard verdict.** STATUS.md:761 already says this of the 80.1 % figure; **it says it nowhere of the 75.5 % figure**, and 75.5 % is what sits in the headline at STATUS.md:160.

**The 75.5 % figure's provenance:** `tables_D2_C.txt:281-298`, C2 −3 dB, **N=1.6e5**: V0 0.593 (0.573, 0.611), V1 0.145, V4 0.154, V4b 0.161, M-ours-bstar 0.252, genie 0.034. `1 − 0.145/0.593 = 75.5 %`; gap to genie closed `(0.593−0.145)/(0.593−0.034) = 80.1 %`. n=2560. gate: **sibling-qualified PASS only** (`d2sx_N160000_a1.pt` has no gate record; PASS inherited from `ckpt/sx_N160000_D1.pt`, `LADDER_C.md:1`). Equal budget: **NO** for the cross-prior comparison (16×); **YES** for the V0-vs-V1 site ablation within the table (same checkpoint). Power: V0→V1 **NO TEST EXISTS**; bstar→V1 in this table is POWERED 3/3 (pooled 511:78 p=5.8e-79) **but at 16× budget asymmetry**.
In the equal-budget tables the same V0→V1 ratio is **81.6 %** (B1e4), **80.4 %** (B4e4), **83.0 %** (B1e4s2 a2). **STATUS contradicts itself across sections: §6g states 81.6/83.0 correctly; the headline at :160 and :747 carries 75.5 % under "같은 체크포인트·같은 예산이므로 공정하다".**

## E4. Pre-registration deviations, disclosed

- **`10_SPEC_stageC.md:197-205` (§3b) fixes the primary result as V0 ALONE** ("주 결과는 V0 하나다"); V1–V3 are secondary mechanism variants. **STATUS.md:672-676 presents the V0 → V1 site ablation as "본 연구의 1차 주장".** That reverses the registered primary/secondary split and I found no `DECISIONS.md` entry recording the reversal.
- **V4 is POST-HOC registered.** `10_SPEC_stageC.md` §3c: *"V1–V3 were registered before results were seen. V4 was NOT. V4 is registered AFTER being observed in the §2 H4 diagnostic cross-experiment."* §3c also required V4/V4b to be built **only from a GATE-PASSING checkpoint** (`N′=1.6e5`); the equal-budget tables build them from gate-FAILED checkpoints, licensed only by the §6d/§6f carve-out.
- **V4b was pre-registered and silently dropped** until the 2026-09-21 18:20 audit caught it; wired the same day (`code/arms.py:174-179` carries the comment). **V4b was never run on D1 at all** — `DECISIONS.md` 2026-09-21 21:45: *"D1's V4b was NOT run - recorded here as a decision, not an omission."* So the cross-testbed symmetry argument does not cover V4b.
- **§6f predictions were NOT blind.** `10_SPEC_stageC.md:551-557`, under the heading `DISCLOSURE BEFORE WRITING THE PREDICTION (IMPORTANT)`, states the predictions were made **after** seeing the non-equal-budget N=1.6e5 C1 and C5 results (bstar → V1: C5 821:674 p=1.6e-04, C1 1402:1602 p=2.8e-04) and are therefore **"WEAK predictions"**, with blinding retained only on "does the same ordering appear at equal budget". **STATUS §6f omits that disclosure and scores them 3/3.**
- **§6h was pre-registered *before reading*, not before running** (see C2): 20-hour gap between the `.npz` files and the prediction commit. Disclosed by the spec itself.
- **§6l's pre-registered prediction was WRONG in our favour:** it predicted K=1024 would win and b* would move at N=1e4. It did not.
- **TABLE C (the pre-registered cross-Tp goodput envelope, 08_SPEC §3) was NEVER COMPUTED.** `tables_D2_B1e4.txt:424` / B4e4 / B1e4s2: `prior S2: cells C1 and C2 are not both present (C1: 0 points, C2: 7 points) -> envelope not computed`. `tables_D2_B1e4x.txt:785`: `(C1: 7 points, C2: 0 points) -> envelope not computed`. **The Tp ≥ 3 envelope rests on three separately-run tables compared by hand.**
- **D2's departure from conditional Gaussianity is engineered** through a DETERMINISTIC path-gain magnitude: `p_l ∝ exp(−l/τ)`, τ=2, Σp_l = 1, deterministic; `α_l = √p_l · exp(jψ_l)` with `ψ_l ~ Unif[0, 2π)`; `L ~ Unif{3..8}`; continuous (ungridded) AoA/AoD, sector ±π/3 for prior S2 (`05_SPEC_testbed_D2.md:18, :23, :25`). **The spec's own note:** *"CAUTION [conjecture, VERIFY]. Standard channels are not necessarily unfavourable to GMMs. The Utschick GMM channel-estimation line exists precisely because of 3GPP channels' conditional-Gaussian structure. Taking CDL as-is could FAVOUR the GMM. D2's distinguishing feature is not real-channel fidelity but the BREAKING of conditional Gaussianity - do not blur this in the write-up."*

## E5. Retractions on record — do not resurrect

| # | Retracted claim | Replacement | Source of the retraction |
|---|---|---|---|
| R1 | "The learned score's Jacobian matches the exact one to three significant figures on D1." | The reference was an **EM fit (K=32, N=1e4), not D1's true prior**. Surviving claim: PSD everywhere on D1; ties the fitted mixture on the bulk (both inside 2 %); better on the extremes (λmax 4/4, λmin 3/4); **worse on λmin at the largest σ (23.47 % low)**. | `jac_spectrum.txt:29-33` `[CORRECTED 18:40 after audit]`; STATUS.md:213 |
| R2 | "None of GA–GD tests PSD-ness" / "an L2 gate cannot constrain the sign." | By Weyl, `GD < λmin(J*)/‖J*‖_F` **proves** PSD; at D1 k=0 the bound is ≈0.11 and measured GD is 1.6e-3 (68× inside). Surviving: the 0.20 threshold is too loose for D2, and `f(λmin(Herm J) < 0)` — measurable on D2 **without ground truth** — is not in GA–GD. | STATUS.md:178, :214 |
| R3 | "The repaired learned prior beats the fitted GMM at every SNR / all 7 SNRs." | **5 wins / 1 loss / 1 tie.** Loss at +9 dB (0.0039 vs 0.0000), tie at +15 dB. Also "3.5×" (0.031 vs 0.109) is the **n=64** table; the n=256 sweep gives 0.043 vs 0.090 ≈ **2.1×**. | `settling_D2.txt` `[CORRECTED 18:40 -- the heading previously read AT EVERY SNR]`; STATUS.md:215 |
| R4 | "The learned arm ties the exact-score oracle." | **No such paired test was ever run.** It was two arms each compared to a common third (R2-ours-G) with win counts eyeballed side by side (learned 449/307/374 vs oracle 449/321/365 on C1/C2/C5). | STATUS.md:201-203 |
| R5 | "asym_reg is decreasing, so the V3 regulariser is working." | Two cherry-picked adjacent points (5.6e-2 → 2.6e-2); the series **oscillates over four orders of magnitude**. GD got **4.8× worse**. | STATUS.md:184 |
| R6 | The margin hypothesis explaining V3 vs Chao et al. (ICML 2023, QCSBM). | **Refuted by V3's own data**: V3 also failed on D1 where λmin = +0.94 and margin is ample, with GB, GC, GD all FAIL. Two untested explanations remain: (i) λ=1.0 too large (sweep incomplete, λ=0.1 diverged); (ii) different success criterion (CIFAR sample quality vs GC). | STATUS.md:906-925, `[2026-09-22 08:45 CORRECTION]` |
| R7 | "Gate GD (0.27–0.32 vs tol 0.20) is the gate this checkpoint family failed" — the "the gate that failed is exactly the Jacobian gate" sentence. | **False.** Primary gate record: for this configuration **GD = 0.1499 PASS, GC = 0.2241 FAIL**. The 0.27–0.32 values belong to other ladder rungs (L4u_a3 0.3198, L5_a3 0.3859). **This false sentence is STILL sitting in two source files.** | STATUS.md:300-310 vs `results/diag/h4-jswap_summary.txt` §5 and `jacpsd-counterfactual_SUMMARY.txt` §5; primary record `results/hpo_final_r2.txt` |
| R8 | Terminology: "exact GMM" on D2. | It is the exact score **of a fitted, mis-specified 512-component Kronecker mixture**, not of D2's true prior. `05_SPEC_testbed_D2.md:47`: *"Hscore-exact (true prior's exact score): NONE. Exists on D1 only."* | STATUS.md:333-339 |
| R9 | "Even passing all four gates, a learned prior cannot be used in an EP receiver" (2026-09-21 15:2x text). | **SUPERSEDED** by the 16:30 D1 confirmatory run — the gate-passing checkpoint works at 20 of 21 D1 grid points. File marked *"keep for the record, do not quote"*. | STATUS.md:424-431 |
| R10 | The n=640 D1 confirmatory figures. | **Superseded by the n=2560 run.** Retracted: C2 "V0 → R6-exactEP 7:8 p=1.0", C1 "92:72 p=0.14". Replacements: C5 88:91 p=0.88 POWERED; C2 56:42 p=0.19 UNDECIDED. The pre-registration requires n ≥ 2560 at decision points. | STATUS.md:216 |
| R11 | "b* = kron K=256 … the K grid was extended 128 → 256 → 512 whenever b* sat at the boundary." | `gmm_fit_D2.txt:30` and `:66` both read b* = kron K=512. STATUS's own correction: *"do not write the sentence that we extended the grid in the direction that strengthens the GMM."* §6l later proved interiority **at N=1e4 only**. | STATUS.md:53-62 |

## E6. STATUS.md vs source — every live discrepancy, with the ruling

| STATUS claim | Source says | Ruling |
|---|---|---|
| §6f: `nan` in the BLER column for V0/V1/V4 at C1 −3 dB; "평균 BLER을 정의할 수 없다" (~line 1073) | `tables_D2_B1e4x.txt:74-76`: BLER@16 = **1.000 / 1.000 / 0.996**; detail rows `:91-93` give BLER@1/@2/@8/@16 = 1.000 1.000 1.000 1.000. **BER@16, `ok=`, `tauL@1` are nan.** | **SOURCE WINS** [X1] |
| §6f (~:1075): "F3 가드 2560/2560" for V0, V1 **and V4** | `guard_D2_B1e4x.txt:20-21`: **V4 = 2552/2560 = 0.997**. V0 and V1 are 2560/2560. | **SOURCE WINS** [X6] |
| §6f (~:1116): "GMM·고전 arm은 두 셀 전 격자에서 발동 0건" | `guard_D2_B1e4x.txt` records M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32 and R3-bigamp all firing (rates 0.000–0.002, worst NMSE up to 1.775e+04). | **SOURCE WINS** — correct phrasing is STATUS's own earlier one: "effectively zero, max 0.002" |
| §6f guard summary: V1's C1 rates "+3 0.030, +9 0.172, +12 0.198" | Omits **+6 = 246/2560 = 0.096** and the **MAXIMUM +15 = 522/2560 = 0.204**. | **SOURCE WINS** — quote 0.204, not "up to 19.8 %" |
| :825 and `10_SPEC_stageC.md:453`: "ckpt/d2sx_N10000_a1.pt failed the pre-registered gate (GC 0.243)" | No such measurement exists on that file. Every table header: `NO GATE RECORD mentions d2sx_N10000_a1.pt -- UNVERIFIED here`. GC 0.24333 is from `samplecx_D1.txt:28`, a **D1** checkpoint at the same N_train. | **SOURCE WINS** — the FAIL reaches the D2 arm only through the §5 sibling rule. Same for N=4e4 (0.167) and the N=1.6e5 PASS. |
| :160 / :747: "75.5 % 개선" in the headline, under "같은 체크포인트·같은 예산이므로 공정하다" | 75.5 % is `tables_D2_C.txt`, N=1.6e5. Equal-budget ratios are 81.6 / 80.4 / 83.0 %. STATUS §6g states 81.6/83.0 correctly. | **SOURCE WINS** — the file contradicts itself across sections |
| §6f (~:1098): supports the Tp trend with "C2 0.252→0.145 (−42.5 %), **C5 0.544→0.394 (−27.6 %)**" | For C2, −3 dB **IS** a decision SNR. For C5 it is **NOT** — the C5 bstar→V1 pair is decided at **+9/+12/+15 dB** (`tables_D2_B1e4x.txt:729`). | **SOURCE WINS** — −27.6 % is an untested point estimate outside the decision window; −42.5 % is inside one. Not the same kind of quantity. |
| :312 heads the do() table "n=128" | `h4-jswap_summary.txt:17` "n=64 paired trials"; `jacpsd-counterfactual_SUMMARY.txt` §2 "n=64 paired trials/point". STATUS's own audit item 7 (:216) and the warning at :330 both say 64. | **SOURCE WINS: n=64** [X3, C3] |
| :181 (item 9): "V0 1400/1400 (4.5e+18), V1 1400/1400 (**6.6e+17**), V4 1400/1400 (1.4e+84)" | `guard_D1_C.txt:18-20`: **2560/2560** for all three; V1 worst **1.654e+20**. "1400" appears in no guard file. | **SOURCE WINS** [X7]. Also omits the C1 +3 dB V0 row (11/2560, rate 0.004). |
| :181: "GMM·베이스라인은 어디서도 발동 안 함" | True on **D1 only** (11 arms). On D2 only 5 arms never fire. | **SOURCE WINS** — D1-only statement |
| :176 (item 4): `f(λmin<0)` rising "0.977 → 0.992 → **1.000**" with budget | The 1.000 is `logs/jacpsd_N160000.log`, an **epoch-240 session-scoped temp-dir snapshot flagged IRREPRODUCIBLE** (checkpoint no longer exists). On the permanent final checkpoint (`logs/jacpsd_D2_final.log`) k=0 reads **0.992**, so the chain is **0.977 → 0.992 → 0.992 — a tie, not an increase.** | **SOURCE WINS** |
| :177 (item 5): "shift median 2.81 (k=12) → 3.4e-3 (k=13)"; "indefiniteness still 36 % at σ=0.845" | Both from the same irreproducible epoch-240 snapshot. On `logs/jacpsd_D2_final.log`: k=12 **1.516e-02**, k=13 **1.639e-02** — **no two-order cliff**; k=19 f<0(Jr) = **0.297**, f<0(Herm J) = 0.078. | **SOURCE WINS** — qualitative claim survives, digits do not |
| :278 attributes "255/256, shift median 1.87" to `results/diag/jacobian-psd_*` | That glob's 20-point file `jacobian-psd_D2.txt` is **n=64** where k=6 reads f<0(Herm J) = 0.969, shift_med = 1.813. The 255/256 and 1.87 live in `jacobian-psd_split_D2_k6.txt` (n=256). | **SOURCE WINS** — wrong source label would mismatch n and numbers |
| §6l: "재시딩 9372회" | The selected restart (ll_val −23.5726) has **n_reseed = 9144**. 9372 is restart 0 (ll_val −23.833, not selected). | **SOURCE WINS: 9144, or drop the count** [X10] |
| §6l headline "b* 는 움직이지 않는다" | Holds at **N=1e4 only** (STATUS :1157-1159 does say so). At N=4e4 and N=1.6e5 b* is still grid-edge with +2.36 and +3.78 nat being gained. | Both statements must travel together |
| §6f (~:1110): V4b's C2 BLER@16 at −3 dB = 0.161 | `tables_D2_B1e4.txt:73` (the equal-budget run §6f is about) reads **0.162** (0.148, 0.176). 0.161 is `tables_D2_C.txt:294`, the N=1.6e5 run. | **Attribution error, not a wrong number** [X4] |
| :39 attaches **p = 2.2e-236** to R2-ours-G → R4-scvamp | `tables_D2.txt:792`: pooled **11:1335, p = 0 (double underflow)**. **p = 2.2e-236 exists in NO results file** — grep of the whole `conf` tree returns it only in STATUS.md. | **SOURCE WINS — 2.2e-236 is NOT QUOTABLE.** Write p < 1e-300. |
| :33-40 table headed "D2 C2" contains the row "R4-llr → R4-scvamp … 1.2e-07" | That is the **C1** block (`tables_D2.txt:746-751`) and it is **UNDECIDED**. The genuine C2 value is pooled 335:19 p = 7.8e-76, POWERED (`:798`). | **SOURCE WINS** — wrong on both the cell and the power verdict |
| :47 gives the Module H headline as "D2 C2, n=2560 (결정점)" | `tables_D2.txt:189`: C2 n per SNR = [2560, 2560, **640**, 640, 640, 640, 640]. The +3 dB decision point is n=640. Same overstatement affects R1-turbo → R2-ours-G, where **two** of three decision points are n=640. | **SOURCE WINS** [X11] |
| STATUS §6d heading: "pre-registered paired tests (3-decision-point rule, **ALL POWERED**)" | `tables_D2_B1e4.txt:391-414` contains **7 UNDECIDED pairs**. The six rows STATUS prints are POWERED; the seven it omits are not. Same for B4e4 and B1e4s2. | **SOURCE WINS** — the blanket heading is false |
| `results/jac_spectrum.txt:173` itself prints a "D2 asym" row (1.8e-1 / 2.6e-1 / 2.6e-1 / 1.6e-1) with **NO budget label**; asserts "f(λmin<0) = 1.000 for σ ≤ 0.2"; the next paragraph's "falls to 0.36" comes from a **different checkpoint**. | Row matches `logs/jacpsd_N40000_a1.log` (N=4e4) and no other. On that log k=0 reads **0.992**, not 1.000. The 0.36 is the epoch-240 N=1.6e5 snapshot (k=19 = 0.359). | **One sentence, three checkpoints, one unlabelled row → NOT QUOTABLE as printed** |
| `samplecx_D1.txt:29` "clears all four gates"; `samplecx_D1.txt:41` / `gate_D2.txt:11` "959 configurations (hpo_D1.txt)" | `gate_D1_C.txt:20` + `LADDER_C.md:1`: GA structurally zero, PASS rests on GB/GC/GD. `hpo_D1.txt:16`: **724 trials**. | **Gate-record files win on gates. The 959 is unreconstructible** [X9] |
| `results/diag/sigma-coverage_D2_C1_n8.txt:13` self-labels `C1 (8x4 T=16 Tp=4)` | C1 is **Tp=2** (`code/common.py:53`). The header string is hardcoded at `code/diag_sigma_coverage.py:130` and ignores `--cell`, so **every file that diagnostic produces mislabels Tp as 4**. The physics confirms Tp=2 (high-SNR floor `c̄(Nt−Tp)/Tp` = 1.000 for Tp=2, exactly 0 for Tp=4; measured +15 dB ν_q = 1.015). | **The cell is C1 with Tp=2; the header is wrong** [X14] |
| `tables_D2_C.txt:41` records V4b as `N_train=10000 -- unclassified arm` while its siblings V0/V1/V4 are N_train=160000 | `code/arms.py:172-179` builds V4b from the **same `score_prior_c` object**; `code/runner.py:258` is the source of the fallback string (V4b is in no classifier list). | **CODE WINS** [X5]. `figs/F11` correctly declines to resolve it ("That is what the file says; this figure does not resolve it"). |

## E7. PENDING — runs not yet landed

| # | What is missing | What will fill it | Current state |
|---|---|---|---|
| **P1** | **`tables_D2_B16e4.txt`** — the equal-budget N=1.6e5 comparison. **This is the only run that would make a headline both gate-qualified AND equal-budget.** | The N=1.6e5 GMM EM fit completing for Nr=8, then a BLER run at N_train=160000 for every arm. | **Does not exist.** `results/gmm_fits_D2_n16e4/` was still being written while the verifiers read it. As of my read: **Nr=8 kron K=128 missing** (full family K=16…512 complete); **Nr=4 kron K=64/128/256 missing**. **No authored summary `results/gmm_fit_D2_n16e4.txt` exists** — every N=1.6e5 GMM likelihood in §D1 above is my own computation from the `.npz` files. `DECISIONS.md` 2026-09-22 12:55 flags a live hazard: `arms.load_fits` **silently accepts a partial grid** and `gmm_selection` then picks b* from the reduced set — the same failure path as the 05:55 BLOCKER. **Until `check_fits_n16e4.sh` passes for Nr=8, no B16e4 number should be quoted.** |
| **P2** | **Seed a3** — `tables_D2_B1e4s3.txt`. §6g pre-registered **three** seeds. | A table built from `conf/raw_B1e4s3/` and `ckpt/d2sx_N10000_a3.pt`. | **Does not exist.** `conf/raw_B1e4s3/` and the symlink `results/gmm_fits_D2_B1e4s3` exist; **no table does.** Seed robustness currently rests on **two** seeds, and a2 re-randomises only the diffusion checkpoint. |
| **P3** | **K=1024 at N=4e4 and N=1.6e5** — the fits that would establish whether b* moves off the grid edge at the larger budgets. | `code/fit_k1024_big.sh` completing into `results/gmm_fits_D2_K1024n40000/` and a matching N=1.6e5 directory. | **N=4e4: launched 14:04 KST today, directory exists and is EMPTY. N=1.6e5: not started.** Until they land, "b* is interior" is a statement about N=1e4 and nothing else, and `01_RULES:76` is not satisfied at the larger budgets. |
| **P4** | **The λ sweep** that would separate "λ=1.0 is too large" from "the penalty does not work here". | A λ < 1.0 checkpoint that **completes and is gated**. | **Incomplete.** λ=0.1 attempt 1 diverged at epoch 100 (best val 7.456974e-01 @44); λ=0.01 not reported. **No λ < 1.0 checkpoint has ever been gated.** `LADDER_L0.1.md`. |
| **P5** | **C1 and C5 at N=4e4 and N=1.6e5** — `10_SPEC_stageC.md` §6f promised these. | `tables_D2_B4e4x.txt` and an N=1.6e5 cell sweep. | **Do not exist.** Only `tables_D2_B1e4x.txt` (N=1e4). STATUS §6f does **not** annotate the missing budgets (§6g does annotate "a3 대기"). |
| **P6** | **Test M6** — the pre-registered integrity check whose failure clause is "V1 을 폐기한다". | An M6 row in `results/tests.txt` or `tests_VREV.txt`. | **No recorded result in either file.** [X13] Do not assert M6 either way. |
| **P7** | **TABLE C** — the pre-registered cross-Tp goodput envelope (08_SPEC §3). | A single run holding both C1 and C2. | **"envelope not computed" in all four equal-budget tables.** |

## E8. Declared open items (stated as open by the project)

- **SNR non-monotonicity is only partially explained.** The 6 dB NMSE peak was closed by the §6h sweep (`dscore|eta` NMSE 1.096 at +6 dB; repairs 0.0072–0.0073, monotone). **The C1 high-SNR failure is open**: at +15 dB the first query σ_t = 0.7125 is inside the frozen grid while NMSE is already 197, and divergence precedes grid exit in all three trials that leave it. *"The high-SNR C1 failure has a separate cause that this measurement cannot resolve."* (STATUS.md:347-351, §6j)
- **V2's faster convergence has no measured cause.** Two hypotheses on record — (i) the gradient-field constraint shrinks the search space, (ii) the scalar energy head reduces the output dimension from 64 to 1 and improves the last layer's conditioning. *"NEITHER IS VERIFIED, so neither goes in the paper as a cause. Record the observation only."* (STATUS.md:553-557)
- **V0's larger seed-to-seed spread than V1 was unpredicted and its cause was not measured** (C2 −3 dB: V0 a1 0.789 vs a2 0.881; V1 a1 0.145 vs a2 0.150). Two seeds is not a spread estimate. (STATUS §6g)
- **No measurement separates V0's improving BLER from its worsening Jacobian across budget.** BLER 0.789 → 0.741 → 0.593 while f(λmin<0) goes 0.977 → 0.992 → 0.992 and λmin −0.124 → −0.137 → −0.151. *"improvements in the mean and the score partially offset the site damage. A measurement that separates the two does not exist yet."* **This is an inference from two curves, not a demonstrated trade-off.**
- **The manifold argument is a PREDICTION, not a measurement of D2's true Jacobian, and it was HALF RIGHT.** D2's support is a union of 3L-dimensional sets with L ~ U{3..8}, i.e. 9–24 dimensions in ℝ⁶⁴, co-dimension 40–55. The **near-zero count** (41.1 of 64 at σ=0.256) lands inside the predicted band; the **negative count does not** — it predicted ~half the co-dimension (20–27) and measured 7–20. The source states this explicitly and does **not** identify which of the 64 directions are tangent and which are normal.
- **"The learned near-zero spectrum is closer to the truth" remains UNPROVEN.** D2 has no closed-form prior, so nothing adjudicates. Two ground-truth-free diagnostics (GB′, Hyvärinen) favour the learned model, which makes it **plausible, not proven**; `jac_spectrum.txt` says so in three separate places.
- **The fitted GMM's PSD-ness is not evidence the learned model is wrong.** A full-rank mixture cannot represent a density supported near a low-dimensional set, so its Jacobian stays near the identity and is PSD **for free**. It is a sanity reference for the measurement, not a target.

---

# (F) DO NOT WRITE

Each line is a sentence the evidence does not support, with the measurement that refutes it.

**On the headline**
1. ❌ *"At equal training budget the corrected learned-score site beats the fitted GMM prior."* — **without a cell qualifier.** False on **C1 (Tp=2)**: pooled **1372:1632, p=2.3e-06**, GMM ahead at 2 of 3 decision points, POWERED, equal budget (`tables_D2_B1e4x.txt:588-593`). `10_SPEC_stageC.md:573` names this exact sentence.
2. ❌ *"V1 beats the GMM at 3/3 decision points on C5."* — It is **2 of 3**. At +15 dB the test is **243:276, p=0.16**, leaning the GMM's way (`tables_D2_B1e4x.txt:731`).
3. ❌ *"V1 reduces BLER by 75.5 % over V0 at equal budget."* — 75.5 % is the **N=1.6e5** number (`tables_D2_C.txt`). The equal-budget figures are **81.6 % (N=1e4), 80.4 % (N=4e4), 83.0 % (a2)**.
4. ❌ *"The V0 → V1 site ablation is significant (p = …)."* — **No V0 → V1 paired sign test is computed in any shipped table.** `code/analysis.py:371-397` never pairs two Stage C arms. No p-value, no discordant-pair count, no power verdict.
5. ❌ *"V1 closes 80.1 % (or 85.3 %) of the gap to the genie bound"* stated as a result. — **Every arm-vs-R5-genie pair on C2 is UNDECIDED** under the pre-registered power guard (2 decision points where 3 are required) in **all three** C2 equal-budget tables **and** in `tables_D2_C.txt`. It is a TABLE A point-estimate description only.
6. ❌ *"V1 is the best non-genie arm at equal budget."* — True on **C2 only**. On C5 V1 does **not** beat R2-ours-G (pooled 661:681 p=0.6, not significant); on C1 **R2-ours-G beats V1** at 2/3 (pooled 1107:1498, p=1.9e-14).
7. ❌ *"The primary claim is the V0-to-V1 site ablation, as pre-registered."* — `10_SPEC §3b` pre-registered **V0 alone** as primary. The swap is a post-hoc reordering.
8. ❌ *"V4 is a pre-registered variant."* — `10_SPEC §3c` states V4 was registered **AFTER** being observed in the H4 diagnostic, and requires that fact to appear in the paper.

**On gates**
9. ❌ *"The checkpoint passed four independent quality gates."* / *"passes all four gates."* — **GA is identically zero by construction** (~1e-15 against a 1e-6 threshold). PASS rests on **GB, GC, GD**.
10. ❌ *"The D2 model passed the pre-registered gates."* — **No D2 checkpoint has, or can have, a gate record.** Say "its D1 twin passed."
11. ❌ *"The checkpoints used in the equal-budget runs were gated."* — N=1e4 and N=4e4 **inherit FAIL** (GC 0.2433 and 0.16651 vs 0.15). §6d pre-registered these as budget-axis measurements, not arm results.
12. ❌ *"The gates were satisfied at the registered arm budget."* — At N=1e4, GC = 0.24333 vs 0.15, a factor of **1.62**. Only GB and GD are met. `M-ours-dscore` stays **BLOCKED** on both testbeds.
13. ❌ *"The pre-registered gate battery caught the Jacobian defect."* — It reached the right conclusion (BLOCKED) through the **wrong mechanism**: GC blocked on first-order score error while **GD, the Jacobian gate, PASSED at 0.1499**. Two diagnostic summaries still assert the opposite.
14. ❌ *"The 1e4 failure was a tuning shortfall that more search would fix."* — `10_SPEC_stageC.md:172` names this un-sayable: hundreds of attempts say otherwise, and five of six architecture families are statistically indistinguishable at equal trials.
15. ❌ *"Passing the D1 gate guarantees D2 performance."* — `10_SPEC §8` lists this as un-claimable; **gates are measured on D1 only — state the limit.**
16. ❌ *"Test M6 confirms the PSD projection is inert on the GMM arms."* — M6 was pre-registered with an explicit **discard-V1-on-failure** clause and **has no recorded result**. Do not assert it either way.

**On the baseline**
17. ❌ *"The GMM baseline b* is interior to the K grid, so the classical baseline is fitted to convergence."* — True **only at N=1e4 for Nr=8**. At N=4e4 and N=1.6e5 b* is on the K=512 edge with ll_val still climbing +2.36 and +3.78 nat; Nr=4 was never extended to K=1024 at any budget.
18. ❌ *"We extended the K grid until the GMM was as strong as it could be."* — STATUS.md:60 explicitly forbids this sentence until the N=4e4 and N=1.6e5 extensions land (P3).
19. ❌ *"Enlarging K cannot help the GMM."* — Measured at N=1e4 only, by a **0.099-nat margin on one 5000-sample validation set with no error bar**, against a restart-to-restart scatter of 0.43–0.59 nat at the same K. `code/fit_k1024_big.sh` predicts K=1024 **will** win at the larger budgets.
20. ❌ *"The mandatory control confirms that scalarisation does not help the GMM, so the gain belongs to the learned prior."* — The control is null in **one of four** POWERED, equal-budget blocks (C2 at N=1e4, p=0.16). At C2 N=4e4 (p=1.7e-04), C1 (p=5.7e-13) and C5 (p=3.7e-22) it is **significant, always with the matrix-site GMM winning**.
21. ❌ *"The N=1.6e5 comparison shows the learned prior beating the GMM at equal budget."* — `tables_D2_C.txt` is **16× asymmetric**, stated in its own header and in the F11 caption. STATUS.md:694-697 already committed to not using it as a primary claim.

**On divergence and stability**
22. ❌ *"V1 does not diverge"* / *"the repaired wiring removes divergence."* — V1 fires the F3 guard on **2560/2560 = 1.000** at C1 / −3 dB (worst NMSE 4.153e+23 equal-budget, 3.518e+24 at N=1.6e5) and at rates **rising with SNR on C1 to 0.204 at +15 dB**.
23. ❌ *"V4b is a working scalar-site variant."* — V4b fires the guard on **100 % of trials at every SNR of C1 and C5** with BLER ≈ 0.99. It works only on C2.
24. ❌ *"The GMM and classical arms never diverge."* — On D2 they do: M-ours-bstar up to 3/2560, M-ours-bstar-scalar up to 6/2560 (0.002), M-ours-gmm32 and R3-bigamp 1/2560 each. The "never fires anywhere" statement is **D1-only**.
25. ❌ *"V0 is worse than classical turbo"* quoted as a plain BLER comparison. — V0's BLER is an **average that keeps diverged blocks**: 0.34–0.88 of trials fire the guard depending on cell and SNR. The divergence rate must travel with any V0 BLER number.
26. ❌ *"The pre-registered wiring (V0) works when given enough data."* — V0's BLER improves with budget (0.789 → 0.741 → 0.593 at C2 −3 dB) but is **worse than classical turbo (0.537–0.543) at every budget and every cell**, and its Jacobian does not improve.
27. ❌ *"Magnitude flooring leaves the divergence unchanged."* — `abs1e-2` reduces divergence by roughly an order of magnitude (0.172 → 0.012 at −3 dB) while leaving BLER **completely unrepaired**. That dissociation is itself the evidence that conditioning is not the causal variable.

**On the mechanism**
28. ❌ *"The learned score's Jacobian matches the exact one to three significant figures on D1."* — **RETRACTED** (R1).
29. ❌ *"D2's true Jacobian is near-singular"* / *"the learned near-zero spectrum is fidelity, not noise."* — D2 has no closed-form prior; nothing adjudicates. Plausible, **not proven**.
30. ❌ *"The fitted GMM's PSD Jacobian shows the learned model is wrong."* — A full-rank mixture is PSD **for free** on this geometry.
31. ❌ *"Denoising score matching produces a non-conservative field, and that is why D2 breaks."* — The learned field is **non-conservative on D1 too** (asym 1.9e-3 – 8.4e-2, same order as D2's 0.16–0.28 at the top of the grid), and D1 produces **zero** negative eigenvalues at all 20 points. What separates them is **margin**.
32. ❌ *"The single causal component is the D-14 matrix site fed by the learned Jacobian."* — The source calls this **"one factor short"**: there are **two independently sufficient repairs** (replace J, or change clip from `eta` to `mean`), so the collapse is an **interaction**.
33. ❌ *"The clip fires for the learned denoiser and not for the GMM."* — **CORRECTED**: the GMM's J has λmax>1 on **51–79 %** of held-out q, which also trips the floor. The discriminator is **indefiniteness** (frac λmin<0 = 0.70–1.00 vs 0.000).
34. ❌ *"The belief-mean shift of 4.3e3 to 1.1e5 measures the dose of the damage."* — It is a **MARKER, not a dose**. The fully repaired `dscore|mean` records shift 1.146e+03 at 0 dB while achieving BLER 0.047, and the table's own 12 dB point breaks the shift↔NMSE correspondence.
35. ❌ *"The eigenvalue sign is the whole story."* — `gmmB|flip4` flips signs at the GMM's own magnitude (33× larger) and produces only **0.3008 → 0.4180** at −3 dB / 0.0898 → 0.1172 at +0 dB (n=256), not a collapse. Defensible form: **the sign is the switch, the magnitude sets the gain.**
36. ❌ *"More data makes the D2 Jacobian worse."* — Worse at **2 of 4** σ and better at the other two; the budget axis is **confounded with stopping epoch** (673 / 1051 / 1784); the k=0 chain that looked monotone rests on an **irreproducible snapshot** and is a tie on the permanent checkpoint. `figs/F7` itself calls *"more data does not fix it"* the **weak** reading.
37. ❌ *"Out-of-grid σ queries explain the C1 collapse."* — Sufficient for C1 at **LOW SNR only**. At +15 dB the query is **inside** the grid while NMSE is already 197; all eight trials exceed NMSE 1 by iteration 2 but only three ever leave the grid, and in all three the divergence came **strictly first**.
38. ❌ *"The cause is the query point."* — The decisive control refutes it: the **GMM control is queried further outside the grid** (σ_t 1.046, top +24 %) than the learned arm (0.9993, +18 %) **and stays healthy**. The cause is the conjunction: out-of-grid query **×** a learned model with no training support there.
39. ❌ *"Extending the σ grid would fix C1."* — Untested, and widening after a bad result is what `01_RULES §2` forbids. §6j is a **measurement, not a repair**.
40. ❌ *"Never write 'the Tp<Nt cavity floor explains the C1 failure' unqualified."* — Write: *explains the C1 failure at low SNR; at +15 dB the divergence precedes the out-of-range query and the cause is undetermined.*
41. ❌ *"The do() interventions are statistically powered."* — **No POWERED/UNDECIDED verdict exists for any of them.** The McNemar tests sit at **2 decision points**, below the pre-registered floor of 3 (`08_SPEC_analysis.md:42`), so the guard would read **UNDECIDED** if applied.
42. ❌ *"The §6h 7/7 result is a pre-registered prediction confirmed by a fresh run."* — The seven `.npz` files existed on disk for **~20 hours** before the prediction was written. Pre-registered **before reading**, not before running; the disclosure must travel with the 7/7.
43. ❌ *"The repaired arm beats the fitted GMM at every SNR."* — **5 wins, 1 loss (+9 dB), 1 tie (+15 dB)**, margins of 1 and 0 blocks out of 256. The source ends with the instruction *"do not restate them selectively."*
44. ❌ *"These diagnostics show the learned prior works."* — Every number in the mechanism family **except the D1 spectrum rows** is a diagnostic probe on a **gate-FAILED** checkpoint, is not an arm, and appears in no BLER table. The D1 spectrum rows use a **gate-PASSING** checkpoint whose learned arms nonetheless collapse completely at C1 / Tp=2 / −3 dB (2560/2560, worst NMSE 1.411e+84).

**On V2 / V3**
45. ❌ *"V2's energy parameterisation is what caused the gate failure."* / ❌ *"V3 shows the Jacobian penalty does not work."* — Both D1 twins were trained under the §3d fallback at **lr/3** after two divergences; **no frozen-lr run of either variant ever completed**, and the 3-attempt ladder is exhausted.
46. ❌ *"V2 trains better, so the energy parameterisation is a better prior."* — A DSM **training-loss** observation on a model with no gate and no BLER entry. V0 and V2 differ by **0.003 %** in D1 validation loss and **68 %** in GC.
47. ❌ *"asym_reg decreased under the V3 regulariser."* — **RETRACTED** (R5). GD got **4.8× worse**.
48. ❌ *"The margin hypothesis explains why the Jacobian penalty failed for us but worked for Chao et al."* — **RETRACTED** (R6). The prior-art conflict is currently **UNEXPLAINED**.

**On scope**
49. ❌ *"The equal-budget result is confirmed across three budgets and three cells."* — The budget axis exists only on C2; the cell axis only at N=1e4. **There is no cell × budget grid** (P1, P5).
50. ❌ *"The result is seed-robust across three seeds."* — **Only a1 and a2 exist** (P2), and a2 re-randomises **only the diffusion checkpoint** — the GMM, Gaussian, classical and control rows are byte-identical to a1.
51. ❌ *"The three cells show a monotone Tp trend at matched operating points."* — The three cells are evaluated at **different decision SNRs** (C2 −3/+0/+3; C5 +9/+12/+15; C1 +6/+12/+15) because the anchor rule reads them off each cell's own baseline curve. **The trend is real; the comparison is not at matched SNRs**, and the pre-registered cross-Tp envelope (TABLE C) was never computed.
52. ❌ Pairing a **−3 dB percentage** with a **pooled p-value drawn from high-SNR decision points** — e.g. "C5 0.544 → 0.394 (−27.6 %), pooled p=0.0011". Those are two different SNR sets.
53. ❌ *"Every comparison in this work is adequately powered."* — **34 pair-level UNDECIDED verdicts are on record** (§D6).
54. ❌ *"Every comparison in the Stage A/B classical table is powered at n=2560."* — Frozen C2 carries n = [2560, 2560, **640, 640, 640, 640, 640**]; C5 carries 640 at every SNR; the C1 R4-llr → R4-scvamp pair is **UNDECIDED**.
55. ❌ Writing ***p = 0*** for a double-underflowed p-value. — Write **p < 1e-300**. And never quote **p = 2.2e-236**, which exists in no results file.
56. ❌ *"D2 is a standard mmWave channel, so the result transfers to real deployments."* — D2's defining feature is **deterministic |α_l|**. `05_SPEC_testbed_D2.md:25` warns that a standard 3GPP/CDL channel could **FAVOUR** the GMM and directs the write-up to frame D2 as *the breaking of conditional Gaussianity*, not as realism.
57. ❌ *"D1 shows learned priors work, and D2 confirms it."* — Three source files carry *"CIRCULAR TESTBED … No claim about learned priors can be made from this table."*
58. ❌ Any C1 statement framed as a within-cell **upper-vs-lower-bound gap** — our own T2c diagnostic records that comparison as **VACUOUS** in C1 (|gap| 0.0337 against a cutoff of 0.05 that is itself **not in the spec**). C1 must be read as **cross-Tp goodput**.
59. ❌ *"The DFT-pilot choice is uncontroversial."* — It is a **knife edge**: erank(Rt) = 0.969 vs erank(C_ens) = 0.890, on **opposite sides of the 0.9 threshold**, and the file states the full-covariance reading would have made the other decision.

---

## NOT QUOTABLE — rows that fail the five-field rule

| item | which of the five is missing / broken |
|---|---|
| **p = 2.2e-236** (STATUS.md:39, R2-ours-G → R4-scvamp) | **Source.** Exists in no results file in the `conf` tree. |
| **`results/jac_spectrum.txt:173` "D2 asym" row** (1.8e-1 / 2.6e-1 / 2.6e-1 / 1.6e-1) | **(iv) equal budget.** The source prints no budget label; it matches `logs/jacpsd_N40000_a1.log` (N=4e4) by numeric match only, which is an inference. Its adjoining "f(λmin<0) = 1.000 for σ ≤ 0.2" is 0.992 on that log, and its "falls to 0.36" comes from a **different** checkpoint. |
| **`results/jac_spectrum.txt:22`** (D2 N=1.6e5 learned, 10.3/17.0/14.1/0.7) | **Irreproducible.** Epoch-240 session-scoped temp-dir snapshot, flagged by the 18:20 audit, **superseded** by the 23:50 addendum. |
| **`logs/jacpsd_N160000.log` figures** — k=0 f(λmin<0) = 1.000; shift median 2.81 (k=12) → 3.4e-3 (k=13); f<0 = 0.36 at σ=0.845 | **Irreproducible.** The checkpoint no longer exists and cannot be re-run. Two of the four D2 f(λmin<0) curves were measured against temp-directory checkpoints. Use `logs/jacpsd_D2_final.log`. |
| **GB′ report** (`results/gate_D2.txt`, nmse_diff/nmse_gmm 0.5204 – 0.8297 across 20 σ points) | **(i) n.** The file header states the testbed, the b*, the report-only status and the gate failure, **but records no n per grid point**. Recover n from `code/gate.py` before quoting, or quote only as "held-out σ grid, 20 points, REPORT ONLY (04_SPEC §6), never used to select anything". Note it is also **denoising**, not the second-order structure the EP site consumes. |
| **"959 configurations"** (`samplecx_D1.txt:41`, `gate_D2.txt:11`, and five table banners) | **Source conflict.** `hpo_D1.txt:16` says **724**, and 959 is not reconstructible (724 + 196 = 920; + 49 = 969). Quote 724 with `hpo_D1.txt`, or "over 900 across two searches" citing both searches. |
| **"gate GD 0.27–0.32 is the gate this checkpoint family failed"** (`h4-jswap_summary.txt` §5, `jacpsd-counterfactual_SUMMARY.txt` §5) | **(iii) gate — factually wrong.** Primary record: GD = 0.1499 **PASS**, GC = 0.2241 **FAIL**. Retracted by STATUS.md:300-310 but still sitting in two source files. |
| **STATUS.md §6f "nan BLER at C1 −3 dB"** | **Superseded by the source**: BLER = 1.000 / 1.000 / 0.996. [X1] |
| **STATUS.md:181 "1400/1400" and V1 worst 6.6e+17** | **Superseded by `guard_D1_C.txt`**: 2560/2560, 1.654e+20. [X7] |
| **`tables_D2_C.txt:41` V4b budget `N_train=10000`** | **(iv) equal budget — wrong in that table.** Code wins: V4b's budget there is N_train=1.6e5. [X5] |
| **The n=640 D1 confirmatory figures** (C2 "7:8 p=1.0", C1 "92:72 p=0.14") | **(i) n.** Below the pre-registered n ≥ 2560 floor at decision points; superseded. |
| **Test M6** | **No result exists** in either test file. Do not assert it in either direction. |
| **Any B16e4 / seed-a3 / K=1024-at-4e4-or-1.6e5 / λ<1.0 number** | **Does not exist yet.** See PENDING P1–P4. |
| **"b* at N=1.6e5" as an authored project result** | **No summary file `results/gmm_fit_D2_n16e4.txt` exists**, and the `.npz` set is **incomplete** (Nr=8 kron K=128 missing). The values in §D1 are my own computation from a live, unfinished directory. |

---

# ADDENDUM (2026-09-22 18:00 KST) — 14:40 시점에 PENDING 이던 항목, 확정분

인용 규칙 5요소를 각 행에 붙였다. 정본은 `source` 열의 파일이다.

| # | 사실 | 수치 | n | testbed·셀·SNR | 게이트 | 동일예산 | power | source |
|---|---|---|---|---|---|---|---|---|
| P1 | **게이트 통과 + 동일예산** 표: V1 이 GMM 을 이김 | V1 0.145 vs GMM 0.253; `bstar→V1` −3 dB 325:49, +0 122:19, +3 42:10, **pooled 489:78 p=1e-73**, 3/3 | 2560 | D2 C2 −3/+0/+3 | 학습 arm `d2sx_N160000_a1` — D1 형제 `sx_N160000_D1` PASS (LADDER_C.md:1); D2 자체 게이트 행 없음 | **예 (전 arm N=1.6e5, b\*=kron K=512, Nr=8 12 구성 전부에서 선택)** | POWERED | `tables_D2_B16e4.txt` |
| P2 | 동일예산 곡선 3점 완성 | V1 0.145/0.145/0.145, GMM 0.252/0.250/0.253 (N=1e4/4e4/1.6e5) | 2560 | D2 C2 −3 dB | 1e4·4e4 FAIL(GC 0.243/0.167), 1.6e5 PASS(형제) | 예 (각 점 내부) | POWERED (각 점) | `tables_D2_B{1e4,4e4,16e4}.txt` |
| P3 | §6f @1.6e5: C5 는 동률, C1 은 GMM | C5 `bstar→V1` +6 232:156, +12 206:213, +15 185:271, pooled 623:640 p=0.65 (1/3 대 1/3); C1 1109:1691 p=3.1e-28 GMM 3/3 | 2560 | D2 C5 +6/+12/+15; C1 +6/+12/+15 | 형제 PASS | 예 | POWERED | `tables_D2_B16e4.txt` |
| P4 | 동작 범위 문장 (게이트 통과 예산) | "Tp=4 전 SNR / Tp=3 ≤ +6 dB (−3: 0.400 vs 0.517) / Tp=2 열세" | 2560 | D2 | 형제 PASS | 예 | — | STATUS §6f@1.6e5 |
| P5 | 시드 강건성 3/3 | V1 −3 dB 0.1453 / 0.1496 / 0.1477 (a1/a2/a3), 전부 a1 CI [0.132,0.159] 안; V0→V1 81.6/83.0/81.8%; a3 pooled 495:64 p=1.5e-83 | 2560 각 | D2 C2 | FAIL (N=1e4) | 예 | POWERED | `tables_D2_B1e4s{2,3}.txt` |
| P6 | §6p: C2 에서 V1 이 11 SNR 전부 우세, 가드 0 | −9 41:3, −7 312:30, −6 544:56 p=2e-101, −5 567:94 | 2560 | D2 C2 −9…+15 | FAIL (N=1e4) | 예 | 앵커 규칙 2점 → UNDECIDED; §6p 규칙(4점 자체) 로 SNR 별 검정 | `tables_D2_B1e4lo.txt`, `lowsnr_6p_score.txt` |
| P7 | §6p 예측 채점 | 1 빗나감(비 단조 감소), 2 빗나감(C2 −9 무붕괴), 3 적중(C5 −5 생존·−6 붕괴), 4 반 | — | — | — | — | — | STATUS §6p |
| P8 | gap 최대점 (척도별) | 절대차 **−6 dB** 0.791→0.601 (0.190); 비 **+6 dB** 0.0125→0.0039 (3.2×); 판정점 −3 dB 1.74× | 2560 | D2 C2 | FAIL (N=1e4) | 예 | −3 만 3점 POWERED | `figs/F14{a,b,c}_*.txt` — **b·c 는 사후 선택 (캡션 명시)** |
| P9 | §6l: K 두 배에 GMM BLER 불변 | K=512 0.2504 → K=1024 0.2500 (−3 dB), 전 SNR ±0.002; ll_val −17.34 → −15.88 | 2560 | D2 C2 | FAIL (N=4e4) | 예 | — | `tables_D2_B4e4k1.txt` (raw meta `kron_K=1024`) |
| P10 | §6e λ 스윕 게이트 | λ=0.01 PASS (GB +0.32%, GC 0.0991, **GD 0.0887 > V0 0.0718**); λ=0.1 FAIL (0.065/0.369/0.319); λ=1.0 FAIL | n_eval 512, n_jac 64 | D1 | — | — | — | `gate_D1_L{0.01,0.1}.txt`, `LADDER_L*.md` |
| P11 | §6e asym 대 PSD | λ=0.01 asym 0.79× V0 이지만 σ=0.79 에서 lmin −0.089, f<0 0.938; λ=0.1 σ≥0.48 부터 f<0 0.88~1.0; V0 20점 전부 PSD | 128/점 | D1 σ 격자 20점 | — | — | — | `logs/jacpsd_D1_lam{0.01,0.1}.log` |
| P12 | A8 복잡도 | Module H 1회: GMM K=512 17.1 ms, 학습 78.8 ms (4.6×); PSD 투영 −0.8% (공짜) | 40/ν | CPU 1스레드 float64 | — | 추론만 | — | `complexity_moduleH.txt` |

**아직 PENDING**: B16e4k (N=1.6e5 를 K=1024 격자로 재확인, 병합 대기), B4e4k (K=2048 격자, 적합 중).
둘 다 P9 의 결과로 보아 GMM BLER 이 움직이지 않을 것으로 예상하지만 예상으로 끝내지 않고 측정한다.

**쓰면 안 되는 문장 (추가)**: "Tp≥3 에서 학습 prior 가 낫다" (P3·P4 — Tp=3 은 SNR 조건 필요) ·
"gap 최대점을 예측했다" (P7 — 문면 예측은 빗나갔다; −6/+6 은 사후 선택) · "λ 페널티는 λ 가 작으면 도움이 된다"
(P10·P11 — GD 가 나빠지고 부호가 망가진다) · "K 를 늘리면 GMM 이 따라온다" (P9 — 안 온다).
