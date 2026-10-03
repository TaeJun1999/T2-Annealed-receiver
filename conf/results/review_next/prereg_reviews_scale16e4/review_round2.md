# NEXT_EXPERIMENTS_SCALE16e4 — 2차 적대적 검토 원문 (v2 대상; Fable 서브에이전트 3 렌즈)

출처: 워크플로 출력 `wf_scale2_v2.json` 의 `reviews` 배열을 필드 순서대로 옮긴 것이다(문구 무수정; 렌즈마다 반드시·권고·v1 미해결·확인). 반영 내역은 등록 문서 머리의 "v2 → v3 변경 요약". 1차 원문은 `review_round1.md`, 3차(v3 검증)는 주 세션이 추가한다.

## review stats

### 반드시 (must)

#### stats2-1

- **section**: §1 다중성 행 (NEXT_EXPERIMENTS_SCALE16e4.md:135) + §2.1 (T0-Holm) 행
- **problem**: (T-iv) 인 데이터셋의 Holm 순서가 정의돼 있지 않다. 현재 문장 "p 가 작은 쪽이 첫째 … 첫째가 0 을 포함하거나 (T-iv) 이면 둘째는 자동으로 (T0-Holm)" 은 (T-iv) 가 첫째일 수 있음을 전제하는데, 학습 실패·수용 실패면 p 자체가 없고(순서 불가), 정의 불가 복제 >5 % 가드면 그 결함 있는 부트스트랩의 p 로 순서가 정해진다. 어느 쪽이든 전사자가 결과를 본 뒤 순서를 고르게 된다 → 다른 데이터셋이 95 % 인지 (T0-Holm) 인지가 사후 선택이 된다.
- **fix**:

§1 다중성 행 전체를 다음으로 교체: "**Holm m = 2, FWER 0.10 양측** (PARETO §1 선례). **(T-iv) 인 데이터셋은 p := 1 로 둔다**(가드가 수치 p 를 남기더라도). p 가 작은 쪽이 첫째이고, 동률이면(두 p 가 모두 정의된 0.0000 동률 포함) D2 가 첫째다. 첫째는 95 % CI, 둘째는 90 % CI 로 판정하며, 첫째가 0 을 포함하면 둘째는 자동으로 **(T0-Holm)** 이다. 한쪽이 (T-iv) 면 그쪽은 항상 둘째(라벨 (T-iv))이고 다른 쪽은 첫째로 95 % CI 판정이다; 첫째가 (T-iv) 인 경우는 둘 다 (T-iv) 일 때뿐이다. m = 2 는 고정한다." §2.1 (T0-Holm) 행의 "첫째가 (T0)·(T-iv)" 를 "첫째가 (T0)" 로 고친다.

#### stats2-2

- **section**: code/run_scale2.sh (4) trend 블록 (`if [ -n "${DP[NR32B16e4]}" ] && [ -n "${DP[U28NR32B16e4]}" ] && [ -n "${DP[U28NR16B16e4]}" ]`) + §1 실행 스크립트 행
- **problem**: 두 가지가 §1 가드 행("그 셀을 쓰는 통계량만")과 어긋난다. (1) 세 DP 가 모두 있어야 추세 블록이 돌므로 UMi28 C6 하나에 판정점이 없으면 C6 를 쓰지 않는 D2·UMi28 1차까지 건너뛴다 → 전사자가 frontier_ci 를 손으로 돌려야 하고 명령 원문·spec 순서가 등록 파일 밖으로 나간다. (2) 판정점 개수 검사가 없다: `dp` 가 2 개를 돌려주면 그대로 2 점 R_dp 로 1차·2차 파일이 생성된다(가드 "판정점 3 개 미만 → (T-iv)" 를 결과가 나온 뒤에 사람이 적용하게 됨). 스크립트는 실행 중 수정 금지 대상이 아니므로 동결 커밋 전에 고칠 수 있다.
- **fix**:

trend 블록을 다음으로 교체(줄별 게이트 + 정확히 3 점):
```
dp3 () { local t; for t; do [ "$(echo ${DP[$t]} | wc -w)" -eq 3 ] || { st 1 "trend line SKIPPED (guard: $t decision SNRs '${DP[$t]}' != 3 -> (T-iv) / 판정하지 못함)"; return 1; }; done; }
for LV in 0.95 0.90; do
  dp3 NR32B16e4 && fci scale2_primary_D2_L${LV#0.} NR32B16e4,BRB16e4k --recovery "raw_NR32B16e4:C9:$(csv ${DP[NR32B16e4]})" "raw_B16e4k:C2:-3,0,3" $Q_D2 --rstar 0.05 --level $LV
  dp3 U28NR32B16e4 && fci scale2_primary_U28_L${LV#0.} U28NR32B16e4,BRU28 --recovery "raw_U28NR32B16e4:C9:$(csv ${DP[U28NR32B16e4]})" "raw_U28B16e4:C2:3,6,9" $Q_U28 --rstar 0.05 --level $LV
done
dp3 NR32B16e4 && fci scale2_step_D2_S2 NR32B16e4,BRNR16 --recovery "raw_NR32B16e4:C9:$(csv ${DP[NR32B16e4]})" "raw_NR16B16e4:C6:-3,0,3" --rstar 0.05
dp3 U28NR16B16e4 && fci scale2_step_U28_S1 U28NR16B16e4,BRU28 --recovery "raw_U28NR16B16e4:C6:$(csv ${DP[U28NR16B16e4]})" "raw_U28B16e4:C2:3,6,9" --rstar 0.05
dp3 U28NR32B16e4 U28NR16B16e4 && fci scale2_step_U28_S2 U28NR32B16e4,U28NR16B16e4 --recovery "raw_U28NR32B16e4:C9:$(csv ${DP[U28NR32B16e4]})" "raw_U28NR16B16e4:C6:$(csv ${DP[U28NR16B16e4]})" --rstar 0.05
```
(else 분기 삭제.) §1 실행 스크립트 행 "게이트:" 문장 뒤에 추가: "추세의 각 줄은 그 줄이 쓰는 새 셀의 판정점이 **정확히 3 개**일 때만 돌고, 아니면 그 줄만 건너뛰어 fail 로 센다(가드 (T-iv) / 판정하지 못함; 다른 줄은 영향 없음)."

#### stats2-3

- **section**: §1 한정어 Q-K 행 + §2.1 Q-K (2) + run_scale2.sh `qk` / primary fci 줄
- **problem**: Q-K 의 섭동 방향이 라벨에 유리한 쪽으로만 작동한다. (T+) 의 최악 경우는 C9 끝만 b* 가 좋아지는 것(R_C9↓, ΔR⁺↓)인데, 등록된 실행 (a) 는 두 끝을 동시에 외삽하고 D2 C2 끝의 c_K = 5.264·ΔF_K = +35 는 이미 기록값이라 R⁺_C2 ≈ 0.346 으로 내려간다(동결 전에 계산됨, 검증 확인). 따라서 D2 의 "[K 상한 강건]" 은 C9 의 외삽이 얼마든 R⁺_C9 ≳ 0.5 이면 자동 성립한다 — 한정어가 원래 물으려던 것(fair-2: "K 상한 미적합 잔여가 Nr 와 함께 커져 추세를 만드는가")을 검사하지 못하고, §6 에 "강건" 이 적히게 된다. 설계가 한정어를 미리 정한 것이므로 공개만으로는 부족하다.
- **fix**:

§2.1 Q-K (2) 를 다음으로 교체: "(2) 그 밖에는 세 실행 — (a) 두 끝 `--extrap K2_C9 K2_C2 --ck c_C9 c_C2`, (b) C9 만 `--extrap K2_C9 - --ck c_C9 -`, (c) C2 만 `--extrap - K2_C2 --ck - c_C2` (K_max 가 내부인 끝은 원래 '-'; 두 자리 다 '-' 면 외삽 없음과 같은 출력) — 의 R1⁺ − R2⁺ CI (Holm 수준)에 §2.1 규칙을 적용한 L⁺ 가 **셋 모두** 1차 라벨과 같을 때만 '[K 상한 강건]' (b*⁺ = b* 인 셀은 '(K/2 가 더 낫지 않음, ΔF_K = …)' 병기); 하나라도 다르면 '[K 상한 민감: 실행 (a)/(b)/(c) 의 b*⁺ 에서 <L⁺>]' (다른 실행을 모두 나열). (b) 는 (T+) 의, (c) 는 (T−) 의 최악 방향이다." §1 Q-K 행 끝에 같은 세 실행을 명령 원문으로 적고 출력 파일 `scale2_primary_{D2,U28}_L{95,90}{,_qkC9,_qkC2}.txt` 를 고정. run_scale2.sh: `qk` 뒤에
```
qk1 () { [ -n "$1" ] || return 0; set -- $1; echo "$1 $2 - $4 $5 -"; }   # C9 only
qk2 () { [ -n "$1" ] || return 0; set -- $1; echo "$1 - $3 $4 - $6"; }   # C2 only
```
을 넣고 LV 루프 안에 두 데이터셋마다 `fci scale2_primary_<d>_L${LV#0.}_qkC9 <같은 게이트> --recovery <같은 spec> $(qk1 "$Q_<d>") --level $LV` 와 `…_qkC2 … $(qk2 "$Q_<d>") …` 두 줄을 추가한다(`--rstar` 는 (a) 에만). 예측 12 는 그대로 채점 가능(ΔF_K 정의 불변).

### 권고 (should)

1. §0.1 표의 R*@0.05 CI 수준이 셀마다 다르다: D2 C2·C6 는 90 % 로 보이고 UMi28 C2 만 '[95% 0.102, 0.340]' 이다(SE 0.061 과는 정합). 셋 다 같은 수준(90 %)으로 적거나 수준을 셀마다 명기할 것.
2. 보고 전용 ΔF_K (D2 C6 `K2NR16B16e4`, UMi28 C6 `K2U28NR16B16e4`) 를 계산하는 호출이 run_scale2.sh 에 없다(K2 raw 를 돌리고 수용만 한다). 보고 전용 한 줄을 추가: `frontier_ci.py --recovery "raw_U28NR16B16e4:C6:<dp>" "raw_NR16B16e4:C6:-3,0,3" --extrap <raw_K2U28NR16B16e4 또는 -> raw_K2NR16B16e4 --ck <c_K 또는 -> 1 > results/review_next/scale2_report_C6_dFK.txt` (2차 단계 라벨에는 쓰지 않음을 머리말에).
3. §0.1 "p 모두 0.0000" → B = 2000 이라 p 의 해상도가 0.0005 이므로 "p < 0.001 (부트스트랩 해상도 1/2000)" 로. 같은 이유로 1차 두 p 가 모두 0.0000 동률이 될 가능성이 높아 실제로는 동률 규칙(D2 첫째)이 Holm 순서를 정할 것임을 §1 다중성 행에 한 줄 공개.
4. `dp()` 정규식은 run_prior_eval.sh 와 같고 11/14 arm 표에서 단일 매치임을 확인했지만, 표 B 줄 형식 `^  M-ours-bstar -> M-ours-dscore-C-V1 .*\[decision-point anchor arm` 에 앵커를 걸어 두면 요약 줄이 추가돼도 다른 쌍의 판정점을 집지 않는다.
5. §1 1차 통계량 행: 재사용 셀의 등록 CI 가 `frontier_ci` 것이라고만 적혀 있는데, 실제로 §6 에 실릴 값은 1차 실행(spec 2 자리, C9 먼저 뽑은 뒤)의 R2 90 % 줄이다 — "등록 CI = scale2_primary_<d>_L90.txt 의 R2 줄" 로 파일까지 고정하면 §0.1 의 recovery_ci 값과 셋째 자리가 달라도 혼선이 없다.
6. 작성자 결정 확인(내 렌즈 범위): (2) R_dp(last) 점추정만 — 보고 전용이라 문제 없음; (3) K/2 수용 실패·K2 구성 불가 → 강제 '[K 상한 민감: 외삽 불가]' — 보수적이고 결정론적, 동의; (6) spec 순서 고정(C9 먼저) — Resampler 가 복제마다 spec 1 키를 먼저 뽑으므로 필요한 고정이며 코드와 일치.

### v1 항목 미해결 (v1_items_unresolved)

- (없음)

### 확인 (verified)

- v1 stats-1 해결: §2.2 가 단계별 독립 3 갈래(증가/감소/판정하지 못함), D2 S1 은 기록값 +0.314 [+0.251, +0.381] 인용·채점 없음, '단조 증가' 는 요약 문구(:172-179).
- v1 stats-2 해결(코드 포함): `_Rplus` 가 max(0, dF) clamp 와 ΣF⁺ ≤ ΣF_g → NaN 을 구현; K/2 b* 열은 `rs.take(raw=base, k, x)` 로 base 키의 캐시 인덱스를 재사용(복제마다 (spec,key) 당 1 회 추첨, 새 난수 없음); `_k2_cols` 가 genie 열 동일을 assert; `--ck inf` 는 argparse 통과 후 'n/a (Q-K undefined)' 출력; 항등 검사(bp == bo) 통과. 정의 불가 이름이 '[K 상한 민감: 외삽 불가]' 로 바뀌었으나 1차 라벨 불변·강제 한정어라 의미 동일.
- v1 stats-3 해결(코드 포함): `snr_at` (Demo/exp_0925_analysis.py:45) = log10 max(BLER, 0.5/n) 선형 보간·첫 하향 교차·flag lo/hi/ok; `_rstar` 는 정렬 격자에서 `np.interp` 로 B_V1·B_g 를 얻고(= 감싸는 두 점), 자체 `Resampler(seed)`·복제마다 s* 재계산·정의 불가 lo/hi/g 개수 출력·CI 는 `--level`; 스모크 0.610017/0.806386/0.218465 를 이 세션에서 재실행해 확인(check_frontier_scale.py ALL PASS, CPU·GPU 숨김, user 21 s / 벽시계 2m27 부하).
- v1 stats-4 해결: §1 보고 전용 행에 Q_d := R_C9 − 2R_C6 + R_C2, λ = ln(ρ_a/ρ_b) (C9,C2)·(C6,C2) 점추정만, ΔF_K 정의; 예측 12·13 이 이를 참조. 예측 12 의 D2 C2 산술 35 ≤ 0.15·(864−488) = 56.4 정확.
- v1 stats-5 해결: 수용 (b)(c)(f) 에 `conf/raw_B16e4` 예외(kron_K 512·ll_val·genie 동일만); 스크립트의 python 검사가 448 파일 meta 와 genie 4 키를 대조. 직접 재계산: raw_B16e4 b* −3/0/+3 = 647/191/61 (899), raw_B16e4k 623/184/57 (864), V1 371/88/29 (488), genie 87/26/12 (125), 두 raw 모두 n 2560, meta kron_K 512 vs 1024 → ΔF_K = +35, R⁺_C2 = 0.3457 (문서 ≈ 0.346). raw_B16e4 는 worktree 에 git 추적(`git ls-files` 1344 파일, C2 448).
- v1 stats-6 해결: §4.2 3b 삭제, §1 EM 경로 행이 결정 4 (PASS 면 그 셀 4096 후보만 일괄, 파일마다 kron_batched 기록).
- r·c_K 재계산 일치: D2 C2 r 0.8403499716975932 → c_K 5.2637007373767215, D2 C6 0.3816292958923848 → 1, UMi28 C2 0.43438450740423645 → 1 (§0.1 표·run_scale2.sh CK_D2C2/CK_U28C2 상수와 동일).
- `ci_p`: q = round(50(1−L), 9) → 0.95 에서 2.5/97.5; p = min(1, 2·min(P[D≤0], P[D≥0])) 유한 복제만; `pct` 가 비유한 값을 걸러 정의 불가 복제가 백분위에 섞이지 않음; R1/R2 줄이 셀별 정의 불가 복제 수를 찍어 5 % 가드 채점 가능; 기존 90 % 줄은 `--level` 과 무관(recovery_diff_U28B16e4.txt 마지막 블록과 바이트 동일 확인).
- argparse 가드: `--extrap`/`--ck`/`--rstar` 는 `--recovery` 필요, `--extrap` 과 `--ck` 는 같은 자리에 '-', c_K < 1 거부 — 문서 ⑤ 서술과 일치.
- run_scale2.sh 1차 명령: spec 1 = C9, spec 2 = C2, `$Q_D2` = `--extrap raw_K2NR32B16e4|- raw_B16e4 --ck <c_K> 5.2637007373767215`, L = 0.95·0.90 두 파일, `--rstar 0.05`; 2차 단계는 큰 Nr 먼저·기본 0.90 — §1 원문과 일치. `qk` 는 K/2 태그 수용 실패 시 Q-K 를 빼고 로그에 남김(강제 한정어 규칙과 정합).
- `dp()` 정규식이 analysis 표 B 줄(`decision SNRs ['-9', '-6', '-3']`, tables_D2_S1D2C9.txt:224)을 정수로 파싱; 11 arm·14 arm 표 모두 'M-ours-bstar -> M-ours-dscore-C-V1' 단일 매치(S1D2C9:223, NR16B16e4:368). `eval_accept --points CELL:s1,s2` 정수 파싱·`--tag TAG:ROLE:SHA:CELLS` 형식이 스크립트 호출과 일치; K2 grid 는 `${KR%,*}` 로 K_max 제외.
- MDE 산술: 90 % CI 폭 0.075/3.29 ≈ 0.023 (D2 C2), 0.079/3.29 ≈ 0.024 (UMi28 C2) — §2.4 서술과 일치; R* SE 0.044/0.061 도 §0.1 CI 와 정합.
- Holm 절차 자체(m = 2, 첫째 95 %·둘째 90 %, 첫째 (T0) 면 둘째 (T0-Holm), 둘째 자체 CI 는 보고 전용)는 PARETO §1 선례와 일치하고 p·CI 가 같은 복제 분포에서 나와 서로 정합(라벨은 CI 로 결정한다고 고정).

## review fair

### 반드시 (must)

#### fair2-1

- **section**: §1 선행 코드 ⑤ (frontier_ci 자체 검사) / code/check_frontier_scale.py
- **problem**: ⑤ 는 자체 검사 ALL PASS 항목으로 "서로 다른 raw 의 genie 정렬(`raw_B16e4` vs `raw_B16e4k`) PASS" 를 적었지만 check_frontier_scale.py 에는 그 검사가 없다 — (3) 항등 검사는 K/2 raw = base raw (`raw_B16e4k` 자기 자신) 만 돈다. 실제 평가에 쓰이는 경로(K/2 raw ≠ base: D2 `raw_B16e4`, UMi28 `raw_K2U28B16e4`, 새 셀 `raw_K2<T>`)의 교차 raw 인덱스 재사용(`take(BASE spec, …)`)·genie assert·dF/c_K 산술은 동결 커밋의 검사에 들어가지 않는다(작성자는 수동 실행만 했다). 직접 실행(`--recovery raw_NR16B16e4:C6:-3,0,3 raw_B16e4k:C2:-3,0,3 --level 0.95 --extrap - raw_B16e4 --ck - 5.2637007373767215 --rstar 0.05`, 42 s): R1·R2·R1−R2 줄 불변, `b*(K/2) 899  dF = +35  c_K = 5.2637  SigmaF+ = 679.77  R+ = 0.346  [90% 0.106, 0.492]  SigmaF+ <= SigmaF_g in 0.0%`, R1+ − R2+ = +0.477 [95% +0.301, +0.787]. 동결 문서가 하지 않은 검증을 한 것으로 적는 것은 기록 오류이고, Q-K 의 실제 경로는 미검증 상태다.
- **fix**:

⑤ 문장의 "서로 다른 raw 의 genie 정렬(`raw_B16e4` vs `raw_B16e4k`) PASS" 를 다음으로 바꾼다: "(6) 교차 raw Q-K(실제 평가 경로): spec 2 = `raw_B16e4k:C2:-3,0,3` 에 `--extrap - raw_B16e4 --ck - 5.2637007373767215` → R1·R2·R1−R2·gaps·Q-OP 줄은 외삽 없음과 바이트 동일, `b*(K/2) 899  dF = +35`, ΣF⁺ = 864 − 5.2637007373767215·35 (= 679.7704741918), 점 R2⁺ = (ΣF⁺ − 488)/(ΣF⁺ − 125) ≈ 0.34568 (부동소수 동일식), R1⁺ = R1, `SigmaF+ <= SigmaF_g` 0 %, genie assert 통과 → **통과** (v2 검토에서 직접 실행: R2⁺ 90 % CI [0.106, 0.492], R1⁺−R2⁺ (NR16 vs B16) +0.477 [95% +0.301, +0.787])". 그리고 check_frontier_scale.py 의 마지막 두 print 앞에 추가(동결 커밋에 포함):

# (6) cross-raw Q-K on the path the primary uses: D2 C2's K/2 raw (raw_B16e4, kron 512) vs the base raw_B16e4k
plain2, o2 = run(NR16, B16, F.B, F.SEED, 0.95)
ext2, o3 = run(NR16, B16, F.B, F.SEED, 0.95, ("-", "raw_B16e4"), ("-", "5.2637007373767215"))
assert np.array_equal(o2["bo"], o3["bo"], equal_nan=True) and o3["rp"][0] == o3["r"][0]   # R draws untouched, R1+ = R1
fp = 864 - 5.2637007373767215 * 35                                                       # same float ops as _Rplus
assert abs(o3["rp"][1] - (fp - 488) / (fp - 125)) < 1e-12, o3["rp"]
r2p = next(l for l in ext2 if l.startswith("  R2+:"))
assert "b*(K/2) 899  dF = +35" in r2p and "SigmaF+ <= SigmaF_g in 0.0%" in r2p, r2p
assert [l for l in ext2 if not l.startswith(("# Q-K", "  R2+", "  R1+ - R2+"))] == plain2
print(f"cross-raw Q-K raw_B16e4 -> raw_B16e4k: {r2p.strip()[:120]}")

실행해 ALL PASS 를 다시 받은 뒤 ⑤ 의 시간(22.7 s)을 갱신한다.

#### fair2-2

- **section**: §1 실행 스크립트 행 (게이트) · 수용 검사 (b) / code/run_scale2.sh (3) `acc $T …`, (4) `fci … NR32B16e4,BRB16e4k` 등, (5) `ok $T`
- **problem**: 새 셀의 추세 게이트 키 `ACC[$T]` 는 A·PIL·ALD 세 태그의 **공동** eval_accept 호출 하나다(run_scale2.sh 713–714행; §1 "새 셀은 A+PIL+ALD 수용 호출"). PIL 이나 ALD 태그만 실패해도(ALD estimate 는 GPU Langevin 단계로 캠페인에서 가장 자주 손본 부분) `fci` 가 그 데이터셋의 1차·2차 추세를 SKIP 하고 라벨은 (T-iv) "수용 실패" 가 된다 — 추세의 입력(A 의 b*·V1·genie)은 모두 수용됐는데도. 이는 같은 행의 규칙 "추세·pair 는 수용된 입력만" 과 어긋나고(PIL·ALD 는 추세의 입력이 아니다), 무관한 태그가 1차 라벨을 (T-iv) 로 바꾸는 경로다. 비용은 eval_accept 재호출 한 번(초 단위).
- **fix**:

run_scale2.sh (3) 의 `acc $T --prior $PR --nr $NR $KARG --ll-val $LL --ref-raw raw_$T --fits-dir … --tag $T:… --tag PIL$SUF:… --tag ALD$SUF:…` 한 호출을 두 호출로:

acc $T --prior $PR --nr $NR $KARG --ll-val $LL --fits-dir results/gmm_fits_D2_$T --grid "full:$FK kron:$KR" --tag $T:best:$BSHA:$CELL   # A alone: (a) grid + meta + ckpt id -> TREND gate
acc ${T}pa --prior $PR $KARG --ll-val $LL --ref-raw raw_$T --tag $T:best:$BSHA:$CELL --tag PIL$SUF:best:$BSHA:$CELL --tag ALD$SUF:best:$BSHA:$CELL   # (b) same fits/em_sec + (d) genie replay -> PAIR gate

(5) 의 `ok $T || { st 1 "pair_baselines $T SKIPPED…"` → `ok $T ${T}pa || { …`. (4) 의 `fci` 게이트 키는 그대로(`$T` = A 단독). §1 실행 스크립트 행의 "게이트: 추세·pair 는 수용된 입력만(새 셀은 A+PIL+ALD 수용 호출, 재사용 셀은 bridge: …)" → "게이트: 추세·pair 는 수용된 입력만 — 새 셀의 **추세 게이트 = A 단독 수용 호출** `results/review_next/<T>_accept.txt` (격자 (a)·meta·ckpt id), **pair 게이트 = A 단독 + A·PIL·ALD 공동 호출** `<T>pa_accept.txt` ((b) fits 실체·em_sec 동일, (d) genie 재생); 재사용 셀은 bridge: … . PIL·ALD 만 실패하면 그 셀의 pair 만 빠지고(§2.3 라벨 \"수용 실패\") 추세는 그대로다 — PIL·ALD 는 추세의 입력이 아니다". 수용 검사 (b) 의 "**A·PIL·ALD·chk 는 한 호출**(같은 fits 실체·em_sec; `eval_accept.py:139`): …" → "**A 는 단독 호출**(격자 (a) 포함; 추세 게이트) `--prior --nr --bstar [--kron-K] --ll-val --fits-dir results/gmm_fits_D2_<T> --grid \"full:<FK> kron:<KR>\" --tag <T>:best:<sha>:<C>`; **A·PIL·ALD 는 공동 호출**(같은 fits 실체·em_sec `eval_accept.py:139`, genie 재생 (d)) `--prior --bstar [--kron-K] --ll-val --ref-raw raw_<T> --tag <T>:… --tag PIL<suf>:… --tag ALD<suf>:…`; chk·K2·last 는 각각 별도 호출". §5 실행 인자 행과 4.1 의 수용 파일 목록에 `<T>pa_accept.txt` 를 더한다.

### 권고 (should)

1. §1 GMM 행·§2.1 에 방향을 적을 것: D2 C2 의 b* 는 kron 1024 격자 끝에서 확장되지 않았다(2048 미적합). ∂R/∂ΣF_b* = (ΣF_V1 − ΣF_g)/(ΣF_b* − ΣF_g)² > 0 이라 미확장(더 나쁜) b* 는 R_C2 를 **올리고**, ΔR_D2 = R_C9 − R_C2 와 S1_D2 에는 **보수적**(T+ 에 불리)이다; Q-K 의 c_K 5.26 은 반대 방향(R⁺_C2 ↓) — 두 방향을 한 문장에 병기.
2. §0.1 K 상한 표에 D2 C2 의 R⁺ CI 를 미리 적을 것: R⁺_C2 = 0.346 [90% 0.106, 0.492] (직접 실행). c_K = 5.26 이 K/2 복제 잡음(dF) 을 5.26 배 증폭해 D2 Q-K 의 R1⁺ − R2⁺ CI 폭이 R1 − R2 의 약 2.5–3 배가 된다는 점을 공개 — §6 독자가 D2 '[K 상한 강건]' 의 CI 폭이 C2 끝에서 온다는 것을 알 수 있게.
3. bridge 게이트(수용 (e), `--ref-arms all`)는 통계량에 들어가지 않는 V0·V4·V4b 를 포함한 14 arm 비트 동일로 1차를 막는다. 지금 미리 정할 것: 게이트 = V0·V4·V4b 를 뺀 11 arm(b*·V1·genie 포함) 비트 동일, V0·V4·V4b 차이는 §6 보고 전용 — 또는 14 arm 게이트를 유지한다고 명시(RGB16e4chk 선례). 결과 뒤에 바꾸지 않도록 어느 쪽이든 지금 고정.
4. §5 '재사용 3 셀 대조 (raw `run|git`, …)': 재사용 raw 셋 모두 `run|git` 키가 없다(raw_B16e4k·raw_NR16B16e4·raw_U28B16e4 의 run| 키는 beta·t_in·seed·iters·n·skip·snr·dtype 만; `run|git` 은 뒤에 추가된 키). raw_B16e4k 는 `meta|stagec_ckpt_id` 도 없다(pre-P0-1). → "STATIC16e4 `chunks-sha:` + ckpt sha256sum + `meta|ll_val|kron`·`meta|kron_K` 대조" 로 바꾼다.
5. 수용 (c) 의 'best.epoch == last.best_epoch' 는 eval_accept 가 검사하지 않는다(`sha256[:16]=`·`role=` 부분 문자열만, eval_accept.py:91–93). §5 의 'TBD(`eval_accept` (c))' → 'TBD(`meta|stagec_ckpt_id` 문자열의 epoch=/best_epoch= 를 A raw 와 last raw 에서 읽어 수동 대조)'.
6. worktree 에 `results/gmm_fits_D2_NR16B16e4` 링크가 아직 없다(run_scale2.sh 전제 `[ -d results/gmm_fits_D2_$BF ]` 가 ABORT). §5 때 ⑥ K2 링크 집합과 함께 `ln -s /home/HTJ/t2/conf/results/gmm_fits_D2_NR16B16e4 …` 를 만들고 4.1 에 적는다. `conf/ckpt` 링크는 미추적(문제 없음).
7. 무관한 수정 2 건의 결정을 동결 줄에 적을 것: `results/gmm_fits_D2_B1e4` 심볼릭 링크가 `gmm_fits_D2` → `/home/HTJ/t2/conf/results/gmm_fits_D2_B1e4` 로 바뀌었고, `results/d2_gbprime_UMi28.csv` 에 0단계 N=1e4 행(비 0.904)이 추가됐다. 제안: csv 는 0단계 기록이므로 포함, 링크는 0단계 스크립트가 필요로 하지 않으면 되돌림.
8. R_dp(last) 점추정을 내는 도구가 없다(LASTARMS 에 b* 가 없어 `recovery_ci raw_<T>last` 는 건너뜀). run_scale2.sh 에 3 줄 python(ΣF_b*(A)·ΣF_V1(last)·ΣF_g 를 판정점에서 합해 `recovery_<T>last.txt` 에 기록)을 넣거나, `M-ours-bstar` 를 LASTARMS 에 넣는다(+4 %).
9. `qk()` 가 '' 를 돌려줄 때(K/2 태그 수용 실패) 강제 한정어가 로그에만 남는다. `fci` 의 출력 파일 머리말에 `# Q-K: [K 상한 민감: 외삽 불가] (K/2 tag failed acceptance)` 를 쓰게 해 라벨 근거가 결과 파일 안에 있게 한다.
10. 수용 (k) (`meta|jobs`·`meta|worker_gb` = WGB) 를 스크립트가 검사하지 않는다. `man` 뒤에 한 줄 python 으로 C9 raw 청크 0 의 두 키를 WGB 와 대조하거나, (k) 를 'run_manifest 출력에서 수동' 으로 적는다.
11. ① `common.py` C9 격자 변경은 실행 중 적합에 무해함을 동결 줄에 근거와 함께 적을 것: fit_gpu.py·gpu_sched.sh·run_fitq.sh·gpu_filler.sh 는 `snrs`/`CELLS[` 를 읽지 않고, edge_rule.sh 의 python 은 arms→common 을 import 하지만 격자를 쓰지 않는다(직접 grep).
12. §1 ALD 행에 적을 것: `ald.py regen` 은 `build_baseline_arms` 로 그 셀의 fits 전부(K_max GMM 포함, C9 는 SNR 워커 7 개 × ≈ 7.4 GB)를 로드하지만 파일럿 내용은 `R5-genie.transmit` 만 쓴다 → tune 이 격자 확정 전에 돌아도 파일럿 내용은 같다(순서는 §1 대로 유지). tune 모드의 RAM 요구(≈ 52 GB)도 비용 행에.
13. §0.1 UMi28 C2 의 R*@0.05 CI 만 95 % ([0.102, 0.340]) 이고 나머지 둘은 90 % — 수준을 맞추거나 표기.
14. §0.1 D2 C6 R_dp CI 는 recovery_ci 의 [0.771, 0.871] 인데 frontier_ci 에서 spec 1 로 두면 [0.771, 0.876] 이다(직접 실행) — '순서에 따라 셋째 자리' 문장의 예시로 이 값을 추가하면 §6 대조 때 혼동이 없다.

### v1 항목 미해결 (v1_items_unresolved)

- (없음)

### 확인 (verified)

- fair-1 해소: §1 Q-K 가 민감도 분석(r, c_K = max(1, r/(1−r)), ΣF⁺ = ΣF(K_max) − c_K·max(0, ΔF_K), 강제 한정어·우선순위)로 재정의됨. fits npz 에서 재계산: D2 C2 r 0.8403499716975932 → c_K 5.2637007373767215, D2 C6 0.3816292958923848 → 1, UMi28 C2 0.43438450740423645 → 1 (문서·run_scale2.sh 상수와 마지막 자리까지 일치). 코드: `_Rplus` clamp, `--ck` ≥ 1/inf 검증, `Resampler.take(BASE spec, key, x)` 가 (spec, key) 캐시로 base 인덱스를 재사용, `_k2_cols` genie assert — 항등 검사(3) 통과 재현, 교차 raw 실행 dF +35 / ΣF⁺ 679.77 / R⁺ 0.346.
- fair-2 해소: §2 머리에 G_d 정의, (T±)·S_d·'등록된 13 개' 문장에 붙임(§2.4 금지 문구에도), §5 에 'tol 정지 파일 수 / 전체' 행.
- fair-3 해소: run_scale2.sh 가 K2·last·chk 를 별도 eval_accept 호출로 돌리고(669–671, 713–719행) eval_accept 는 호출 단위로 (bstar, kron_K, em_sec) 동일을 요구함(common_meta) 확인. 재사용 K2 기대 ll_val 을 main fits 에서 확인: NR16B16e4 kron 2048 61.982398757574266, U28B16e4 kron 2048 5.539276756851168; 두 fits 디렉터리에 1024/2048/4096 후보 `.k0r{0,1,2}` 가 모두 있어 K2 `--grid`(a) 검사 통과 가능. raw_B16e4: C2 448 파일 전부 kron_K 512·ll −14.636106156749378, R5-genie blk_err 0/448 다름, b* −3/0/+3 = 647/191/61 vs raw_B16e4k 623/184/57 (ΔF_K +35), V1 371/88/29·genie 87/26/12 는 두 raw 동일.
- fair-4 해소: worktree HEAD 09a840d7 = main 6b1de688 병합(동결 전 완료). run_scale2.sh 전제: `git merge-base --is-ancestor $FREEZE HEAD && git diff --quiet $FREEZE HEAD -- code ../Demo`, `git log -1 -- scale2_s5.txt == HEAD`(§5 커밋 뒤 커밋 금지), 매 runner 호출 전 HEAD 불변 확인(640행).
- fair-5 해소: `results/gmm_fits_D2_NR32B16e4/fit_S2_Nr32_{fullK16,kronK64,kronK256}_n160000.npz` sha256[:16] = 3cef4eebce4f70f5 / 718afe2dcfef5fd7 / 60e1afc94f59fe75, worktree `results/gmm_fits_D2_probeC9/` 의 같은 이름 파일과 동일(main 에는 probeC9 디렉터리가 없음 — 문서의 상대 경로가 맞다). §0.5·GMM 행·수용 (a) 에 공개.
- fair-6 해소: `results/testbed_UMi28_Nr16.txt`·`_Nr32.txt` 존재, TMXa 1.00086 (s.e. 0.00159) / 0.99787 (s.e. 0.00119) PASS, TMXc·TMXd PASS, 'ALL PASS'; mtime 2026-10-01 00:58:31 / 01:11:16 KST (= 09-30 10:58 / 11:11 CDT), 머리말 git 09a840d7; 허용오차는 testbed_mix3.py docstring 에 첫 실행 전(10:50 CDT) 고정. 결정 10 으로 동결 전제 명시.
- check_frontier_scale.py ALL PASS 재현(CPU 1 프로세스, user 20 s): R*@0.05 0.610017 / 0.806386 / 0.218465, R_dp 점 0.508796 / 0.822785 / 0.150427, 기존 recovery_diff 줄 바이트 동일, 항등·산술 assert 통과.
- σ U28NR16g: `results/sigma_grid_D2_U28NR16g.{txt,npz}` 존재(01:10:30 KST), 머리말 14행 `# SNR set : -6 -3 0 3 6 9 12 15 dB (--snr …)`, n = 64 × 16 × 8 = 8192; sigma.py diff 는 task 집합 치환과 머리말 한 줄만(기본 경로 불변).
- D2 C9 ckpt: sha256sum 앞 16 자리 last `d2sx_NR32_N160000_a1.pt` 1f782042a5ad06b8, best `_best.pt` 3cf5d3eff96f0341 (mtime 01:51 / 01:55 KST = 11:51 / 11:55 CDT) — §0.6·§5 일치.
- edge_rule.sh 원문 = §1 GMM 행 서술: kron 최대 K 병합마다 `arms.gmm_selection` 재판정, b* = kron K_max < 4096 이면 2K 재시작 0–2 + merge(후보 3 대기) 를 gpuq 에 한 번, 4096 이면 DONE(캐비엇), 내부면 DONE; full 은 보지 않음(세 셀 full 최대 256/256/128 내부 확인).
- `arms.load_fits` 는 정확한 파일명(`fit_<prior>_Nr<Nr>_<fam>K<K>_n<ntrain>.npz`)만 로드 → `.k0r*` 후보는 선택에 들어가지 않음(38901 §1 문장과 부합). K_max 를 뺀 K2 링크 집합의 b* 는 두 재사용 셀 모두 kron K_max/2 (61.98 > full 최대 16.61; 5.539 > −1.33).
- 역할 문자열: `score.ckpt_identity` 는 role 키 없는 체크포인트를 'legacy-last' 로(`d2sx_N160000_a1.pt`), score.train 은 last/best 를 기록 → last 태그 role 'last'. RGB16e4chk(14 arm, `--ref-arms all`, bridge 와 같은 CLI 형태)가 `role=legacy-last sha 4443921ce8d5c4a1` 로 ACCEPT OK → BRB16e4k 태그 문자열 타당. `meta|stagec_ckpt_id` 는 `--stagec-ckpt` 가 있으면 항상 기록(runner.py:386) → K2·chk·last·bridge 수용 (c) 가능.
- 작성자 결정 확인: (1) chk = A 의 11 arm 은 필요 — eval_accept `--ref-arms all` 은 키 목록을 참조 raw 에서 가져와 'keys missing in tag' 로 FAIL; (3) K/2 수용 실패 → 강제 한정어는 보수적이고 `qk()` 가 Q-K 인자를 빼는 것과 일치; (4) 메모리 가드 코드: `mem_jobs` = floor(0.8·MemAvailable_GiB / G), jobs = min(cpu, tasks, mj), RUN_META 는 Pool initargs, mj < 1 거부; (6) spec 순서(큰 Nr 먼저)·`--extrap/--ck` 위치가 문서와 스크립트에서 일치, L95·L90 두 파일 생성.
- `dp()` 정규식은 tables 형식(`M-ours-bstar -> M-ours-dscore-C-V1 … decision SNRs ['-3', '+0', '+3']`)에 맞고 run_prior_eval.sh 와 동일; `int(float("+0"))` 처리 확인.
- ① common.py C9 격자 변경은 실행 중 적합에 무해: fit_gpu.py·gpu_sched.sh·run_fitq.sh·gpu_filler.sh 에 `snrs`/`CELLS[` 없음; 현재 C9 = −15..15, DEFAULT_CELLS 제외 유지.
- ALD regen 은 fits 를 `build_baseline_arms` 로 로드하지만 파일럿 npz(b·H·G·sigma2)는 `R5-genie.transmit` 만으로 만들어져 b*/K 와 무관 → tune 시점과 격자 확정 순서는 ALD 파일럿 내용에 영향 없음.
- 동일예산: 모든 runner 호출 `--ntrain 160000`, fits `training_set(...,160000)` 스트림 7 = score 학습 집합; 새 셀 11 arm 대 재사용 14 arm 은 `build_point` 가 전 arm 을 만든 뒤 `--arm` 으로 걸러 시행 스트림 소비가 같음(RGB16e4chk·PILNR16 선례 raw 로 확인). 재사용 K2·bridge 는 원 raw 와 같은 ckpt(sha 대조)·prior·cell·ntrain 로 호출.

## review integ

### 반드시 (must)

#### M1

- **section**: code/run_scale2.sh — (3) 줄 188 판정점 수 가드 + (4) trend 게이트 (줄 225–238)
- **problem**: 줄 225 `if [ -n DP[NR32B16e4] ] && [ -n DP[U28NR32B16e4] ] && [ -n DP[U28NR16B16e4] ]` 가 세 새 셀의 판정점이 모두 있어야만 추세 5 개를 돈다. 한 셀(예: D2 C9)이 가드 (T-iv) 이면 UMi28 1차·S1·S2 까지 전부 SKIPPED 되어 §1 가드('그 셀을 쓰는 1차만 (T-iv)')·다중성('한쪽이 정의 불가여도 m = 2 고정')과 어긋난다 — 스크립트가 등록과 다른 결과를 낸다. 또 §1 가드 '판정점 3 개 미만 → (T-iv)' 를 어디서도 확인하지 않아 판정점 2 개로 K2·last·추세가 그대로 돈다.
- **fix**:

줄 188 을 다음 두 줄로 바꾼다:
  [ "$(echo ${DP[$T]} | wc -w)" -ge 3 ] || { log "$T: decision SNRs '${DP[$T]:-none}' < 3 -> guard (T-iv) / 판정하지 못함 (§1); K2 / last / trend of this cell skipped"; DP[$T]=""; }
  N3=$(( $(echo ${DP[$T]} | wc -w) * 64 )); log "$T decision SNRs (anchor b*, never by hand): ${DP[$T]:-none}"
줄 225–238 (if … else … fi 블록 전체) 을 다음으로 바꾼다 (함수 이름은 `tr` 이 아니어야 한다 — `csv()`·줄 98 이 coreutils tr 을 쓴다):
trend () {  # cells(space-separated) then fci args: run iff every named cell has decision SNRs; else record the skip (§1 guard: only the tests USING that cell are (T-iv) / 판정하지 못함; Holm m = 2 stays)
  local CS=$1 c; shift; for c in $CS; do [ -n "${DP[$c]}" ] || { st 1 "frontier $1 SKIPPED: $c has no (or < 3) decision SNRs -> guard"; return; }; done; fci "$@"; }
for LV in 0.95 0.90; do   # both Holm levels printed (first test 95 %, second 90 %; order by the p on either file)
  trend NR32B16e4 scale2_primary_D2_L${LV#0.} NR32B16e4,BRB16e4k --recovery "raw_NR32B16e4:C9:$(csv ${DP[NR32B16e4]})" "raw_B16e4k:C2:-3,0,3" $Q_D2 --rstar 0.05 --level $LV
  trend U28NR32B16e4 scale2_primary_U28_L${LV#0.} U28NR32B16e4,BRU28 --recovery "raw_U28NR32B16e4:C9:$(csv ${DP[U28NR32B16e4]})" "raw_U28B16e4:C2:3,6,9" $Q_U28 --rstar 0.05 --level $LV
done
trend NR32B16e4 scale2_step_D2_S2 NR32B16e4,BRNR16 --recovery "raw_NR32B16e4:C9:$(csv ${DP[NR32B16e4]})" "raw_NR16B16e4:C6:-3,0,3" --rstar 0.05
trend U28NR16B16e4 scale2_step_U28_S1 U28NR16B16e4,BRU28 --recovery "raw_U28NR16B16e4:C6:$(csv ${DP[U28NR16B16e4]})" "raw_U28B16e4:C2:3,6,9" --rstar 0.05
trend "U28NR32B16e4 U28NR16B16e4" scale2_step_U28_S2 U28NR32B16e4,U28NR16B16e4 --recovery "raw_U28NR32B16e4:C9:$(csv ${DP[U28NR32B16e4]})" "raw_U28NR16B16e4:C6:$(csv ${DP[U28NR16B16e4]})" --rstar 0.05
그리고 `bash -n code/run_scale2.sh` 재확인. 문서 §1 실행 스크립트 행 '게이트' 문장에 '판정점 < 3 인 셀은 K2·last·그 셀을 쓰는 추세만 건너뛴다(다른 데이터셋은 돈다)' 를 덧붙인다.

#### M2

- **section**: §1 수용 검사 (b) (줄 141) + 머리 목록 v1→v2 변경 요약 'fair-3 · integ-5' (줄 13)
- **problem**: 문서는 '(b) A·PIL·ALD·chk 는 한 호출' 이라 쓰지만 `eval_accept.py` 의 `--n`(:51) 과 청크 계획 `plan`(:67) 은 호출 단위라 `--n 40` 인 chk 를 `--n 2560` 인 A·PIL·ALD 와 한 호출에 넣을 수 없다(넣으면 A·PIL·ALD 가 청크 계획 불일치로 FAIL). `run_scale2.sh` 는 이미 chk 를 별도 호출(줄 205)로 돌리므로 문서 ≠ 스크립트 — 수용 절차 원문이 실행과 다르면 §6 전사·기록 감사에서 위조로 읽힌다.
- **fix**:

줄 141 의 문장 "(b) **A·PIL·ALD·chk 는 한 호출**(같은 fits 실체·em_sec; `eval_accept.py:139`): `--prior --nr --bstar [--kron-K] --ll-val --ref-raw raw_<T> --fits-dir results/gmm_fits_D2_<T> --grid "full:<FK> kron:<KR>" --tag <T>:best:<sha>:<C> --tag PIL<suf>:… --tag ALD<suf>:…`; chk 는 `--n 40 --points <C>:<S0> --ref-raw raw_<T> --ref-arms all`." 를 다음으로 바꾼다:
"(b) **A·PIL·ALD 는 한 호출**(같은 fits 실체·em_sec = (bstar, kron_K, em_sec) 일치; `eval_accept.py:94,129`): `--prior --nr --bstar [--kron-K] --ll-val --ref-raw raw_<T> --fits-dir results/gmm_fits_D2_<T> --grid "full:<FK> kron:<KR>" --tag <T>:best:<sha>:<C> --tag PIL<suf>:best:<sha>:<C> --tag ALD<suf>:best:<sha>:<C>`. **chk 는 별도 호출**(`--n` 과 청크 계획은 호출 단위라 `--n 40` 을 같은 호출에 넣을 수 없다; `eval_accept.py:51,67`): `--prior --bstar [--kron-K] --ll-val --n 40 --points <C>:<S0> --ref-raw raw_<T> --ref-arms all --tag <T>chk:best:<sha>:<C>` — chk 의 fits 실체 동일성은 `--ref-arms all` 의 arm 별 비트 대조가 대신한다. (`run_scale2.sh` 줄 203–209: A+PIL+ALD 1 호출, chk·K2·last 각 1 호출.)"
줄 13 을 "**fair-3 · integ-5** → §1 수용 (b): A·PIL·ALD 는 한 호출, chk·K2·last 는 별도 호출(원문); 재사용 K2 기대 ll_val 과 `raw_B16e4` 실체를 §0.1·§5 에 미리 적음." 으로 바꾼다.

### 권고 (should)

1. [비용, 결정 4 실효] `edge_rule.sh` 는 2048 병합 10 분 안에 4096 재시작 3 개를 정확 경로로 gpuq 에 넣고 `gpu_sched.sh` 는 빈 GPU 가 있으면 즉시 띄운다 → 일괄 검사(§4.1 '미실행, 4096 이 발동하는 셀만')는 구조상 4096 시작 전에 PASS 할 수 없어 사실상 정확 경로(≈ 300 GPU·h) 로 확정된다. 지금(2048 병합 전) gpuq 에 세 검사를 넣거나(예: `60 GPU bchk_S2_32 <P> code/em_batched_check_nr.py --nr 32 --prior S2 >> logs/em_batched_check_nr32_S2.log 2>&1`, UMi28 두 줄 동일; 예측 4 가 세 셀 모두 4096 이라 낭비 아님) 아니면 EM 경로 행에 '정확 경로 확정' 으로 적는다.
2. [EM 경로 행] `FIT_KRON_BATCHED=1` 삽입 위치를 원문으로: gpuq 줄 `<prio> <kind> <label> <command…>` 의 **4번째 토큰(명령) 앞**에 붙이고, `flock logs/gpuq.txt.lock` 아래에서, `gpu_sched.sh` 가 아직 가져가지 않은 줄에만; 일부 재시작이 이미 떴으면 같은 K 의 후보 사이 경로 혼용이 생기니 후보별 `kron_batched` 를 §5 에 적는다(`fit_gpu.py:75` 가 배열로 기록).
3. [§4.1 할 일 누락] `results/gmm_fits_D2_NR16B16e4` 링크가 worktree 에 없다(main 링크 필요; `raw_NR16B16e4`·`raw_U28B16e4`·`gmm_fits_D2_U28B16e4` 링크는 있음). bridge 3·재사용 K2 2·새 셀별 PIL/ALD/chk/last/K2 링크 집합도 아직 없다 — 전제 검사가 ABORT 하므로 §4.1 에 '링크 생성' 행을 두고 §5 커밋 전 항목으로 적는다.
4. [수용 (k)] `meta|jobs`·`meta|worker_gb` 는 `eval_accept` 도 `run_scale2.sh` 도 검사하지 않는다. `run_manifest.py` 가 `meta|*` 값 집합을 출력하므로(:47) (k) 를 '`run_manifest` 출력의 `worker_gb` 값 집합 = {WGB}, `jobs` 값 집합 기록(재개로 둘 이상이면 청크 범위와 함께)' 로 고쳐 쓰거나, 스크립트 줄 195 뒤에 C9 태그의 청크 전부를 여는 8 줄 파이썬 검사를 넣는다.
5. [§0.1 표·§1 재사용 셀 행 문구] `raw_B16e4` 의 K 512 fits 와 `raw_B16e4k` 의 kron 512 는 **같은 물리 파일**이다(`gmm_fits_D2_B16e4 → gmm_fits_D2_n16e4`, `gmm_fits_D2_B16e4k/*.npz → ../gmm_fits_D2_n16e4/*`; readlink 로 확인). '다른 fits 실체(… em_sec 49597.8 vs 107957.2)' 는 '같은 물리 파일의 부분집합 링크(12 대 13 파일; em_sec 합만 다름)' 로 고치고, '남는 위험(K 512 fits 파일 자체의 회귀)' 문장은 그만큼 줄인다.
6. [⑤ 문구] '서로 다른 raw 의 genie 정렬(`raw_B16e4` vs `raw_B16e4k`) PASS' 는 `check_frontier_scale.py` 에 없다(항등 검사 (3) 은 raw_B16e4k 대 자기 자신). 한 줄 assert 를 추가하거나(`run(NR16, B16, F.B, F.SEED, 0.95, ("-", "raw_B16e4"), ("-", "5.2637007373767215"))` → `round(o["rp"][1], 3) == 0.346`), 수동 실행 결과로 출처를 고친다(재현: b*(K/2) 899, dF +35, ΣF⁺ 679.77, R⁺ 0.346 [90% 0.106, 0.492]).
7. [비용 행] PIL·ALD 를 미정으로 두지 말고 상한을 적는다: V1-pilot 은 V1 과 같은 급이라 PIL ≈ A 의 V1 몫(C9 셀당 ≈ +750 코어·h 무부하), ALD-pilot 은 첫 청크로 — 합계는 25–80 h 가 아니라 그 두 배에 가까울 수 있음을 공개.
8. [동결 커밋 전제] `results/review_next/prereg_reviews_scale16e4/` 가 아직 없다(검토 원문 복사 필요); `results/scale/` 는 있다.
9. [σ 재측정 명령] 원 측정은 `nice -n 19 taskset -c 191` 로 한 코어였다. `sigma.measure` 는 기본 8 워커 Pool 이라 '같은 명령' 에 taskset 을 그대로 두어야 '한 코어 ≈ 14 분' 과 HISNR 부담 문구가 맞다(비트 동일성은 워커 수와 무관).
10. [R_dp(last)] 계산 도구가 없다 — 전사자 산술임을 (결정 2 행에) 명시하거나 LASTARMS 에 `M-ours-bstar` 를 넣어 `recovery_ci` 가 짝 CI 까지 내게 한다(스크립트 줄 200 이 이미 그 분기를 갖고 있음; +≈4 %).

### v1 항목 미해결 (v1_items_unresolved)

- integ-4 (EM 경로, 부분): 서술은 `edge_rule.sh` 와 일치하지만 '4096 재시작 시작 전에 PASS 파일' 이 될 실행 계획이 없다 — edge_rule 이 2048 병합 뒤 10 분 안에 4096 정확 경로를 큐에 넣고 스케줄러가 즉시 띄우므로 결정 4 의 일괄 분기는 지금 검사를 큐에 넣지 않으면 실효가 없다(should 1).
- integ-5 / fair-3 (수용 (b) chk, 부분): 스크립트는 chk 를 별도 호출로 고쳤지만 문서 (b) 원문과 v1→v2 요약은 여전히 'A·PIL·ALD·chk 는 한 호출' 이다(must M2).
- integ-1 (메모리 가드, 부분): `--worker-gb` 구현·기록·비용 재산정은 됐으나 새 수용 (k) 를 실행하는 도구가 없다(should 4).

### 확인 (verified)

- run_scale2.sh `bash -n` 통과. 스크립트가 쓰는 CLI 플래그 전부 존재: runner run `--testbed --ntrain --prior --cell --stagec-ckpt --n --chunk --snr --arm --pilot-arms --ald-file --tag --worker-gb`(argparse :1188–1252); eval_accept `--tag --ntrain --kron-K --ll-val --n --ref-raw --fits-dir --grid --nr --points(CELL:s,s → int) --ref-arms --prior --bstar`(:45–66); ald.py `regen|tune|estimate --tag --prior --cell --fits-tag --set --ckpt`(:284–288); pair_baselines `--base --pil --ald --est --cell --prior --r0 at1`(:105–108) 와 `SUMMARY-B` 줄(:255); recovery_ci `--raw --cell --snrs`; guard_report `--raw --testbed`; run_manifest `--tag`; frontier_ci `--recovery --level --extrap --ck --rstar`.
- 메모리 가드 코드: `main()` 이 `_init(a.tag)`(:1346) 를 먼저 부르므로 cmd_run 의 `_init(TAG, run_meta)`(:654) 가 태그를 지우지 않는다; RUN_META 는 Pool initargs 와 직렬 경로 양쪽으로 워커에 닿고 `meta|jobs`·`meta|worker_gb` 는 :589 로 npz 에 저장된다; eval_accept 의 태그 간 비교 키는 (bstar, kron_K, em_sec) 만(:94, :129) 이고 `--ref-arms all` 은 `meta|`·`run|` 키를 제외(:101), load_raw 는 청크 간 meta 차이를 경고하지 않음 → jobs/worker_gb 가 태그·청크마다 달라도 수용이 깨지지 않는다. G = 8.0 → floor(0.8·753.9956/8) = 75 재현. `mem_jobs` 는 /proc/meminfo MemAvailable, GiB 단위.
- 실행 커밋 규칙: `runner._git_head`(:457–463) = `rev-parse --short HEAD` + `status --porcelain code ../Demo` 가 비어 있지 않으면 `+dirty`; 스크립트 전제는 같은 경로를 검사하고, FREEZE 조상 + `git diff --quiet FREEZE HEAD -- code ../Demo`, HEAD == `scale2_s5.txt` 를 마지막으로 건드린 커밋, 각 runner 호출 전 HEAD 재확인(줄 130). main 6b1de688 은 scale HEAD 의 조상(⑩ 완료 확인).
- ALD 명령 ↔ ald.py: regen → `results/ald/pilots_<tag>_<set>.npz`(dev = DEV_SKIP0 2560, n 512; test = 0..2559), tune → `tune_<tag>.json`, estimate 가 같은 `--ckpt` 문자열·ckpt sha 를 assert(:253) 하고 `ald_<tag>.npz` 저장, git 기록(:155); regen Pool 은 SNR 점마다 1 워커(C9 7 개 × 7.4 GB ≈ 52 GB, 가드 불필요). pair_baselines `--est` = ALD 추정 태그.
- K2·chk·bridge 수용: 재사용 K2 원천 `gmm_fits_D2_NR16B16e4`·`gmm_fits_D2_U28B16e4`(main) 에 kron 2048 병합 + `.k0r{0,1,2}` 3 개와 kron 1024 후보 3 개가 있어 RG 격자 검사가 가능; `gmm_fits_D2_B16e4k` 는 kron ≤ 1024(2048 없음) → D2 C2 K/2 = raw_B16e4 타당. role 문자열: 키 없는 ckpt → `legacy-last`(score.py:712), `last`/`best` 는 score.train 이 기록(:1026–1027) → `--tag …:last:<sha>` 유효; PILB16e4k 선례(run_pilot16e4.sh:17) 도 `ckpt/d2sx_N160000_a1.pt` + legacy-last.
- `dp` 정규식(run_prior_eval.sh:40 과 동일)을 실제 표에 적용: `tables_D2_NR16B16e4.txt` → `-3 0 3`, `tables_D2_S1D2C9.txt` → `-9 -6 -3`(기록 판정점과 일치). `cellinfo` S0: C6 −3, C9 는 ① 뒤 −12(현재 common.py C9 = −15..15 정수 튜플이라 문자열 비교 `(-12, -9, -6, -3, 0, 3, 6)` 이 ① 뒤 성립하고 그 전엔 ABORT).
- edge_rule.sh 원문 = 문서 GMM 행: 10 분마다 `arms.gmm_selection`, b* = kron 최대 K < 4096 이면 2K 재시작 3 + WAIT merge 를 gpuq 에 한 번, `logs/edge_done_<tag>` 로 DONE, 4096 정지, 로그 edge_rule.log. gpu_sched.sh 는 tmux 안에서 `CUDA_VISIBLE_DEVICES=<g> <command>` 로 띄우므로 명령 앞 `FIT_KRON_BATCHED=1` 접두가 동작; fit_gpu.py 가 `kron_batched` 를 파일·후보별로 기록(:46, :75). 현재 gpuq 에는 2048 줄만 있음(4096 없음). em_batched_check_nr.py 출력명 `nr{nr}b_batched_check_{prior}.txt`, testbed_mix3 `--nr` 출력 `testbed_<prior>_Nr<nr>.txt` 확인.
- `check_frontier_scale.py` 재실행(CPU, 43.8 s 부하 상태) ALL PASS: R\*@0.05 0.610017 / 0.806386 / 0.218465, R_dp 점 0.508796 / 0.822785 / 0.150427. `frontier_ci.py --recovery raw_NR16B16e4:C6 raw_B16e4k:C2 --level 0.95 --extrap - raw_B16e4 --ck - 5.2637007373767215 --rstar 0.05` 실행(40.6 s): b*(K/2) 899, dF +35, ΣF⁺ 679.77, R⁺ 0.346 [90% 0.106, 0.492], genie 정렬 assert 통과, R1 − R2 +0.314 [95% +0.241, +0.393] p 0.0000, 절대 격차 363 [332, 396] / 739 [697, 781] — §0.1·머리 목록의 수치와 일치.
- σ: `sigma_grid_D2_U28NR16g.npz` 키 hi/lo/nu/samples/sigma, σ_hi 0.546964149299485; 추적 파일 `results/sigma_grid_D2_U28NR16.npz` 의 7168 표본이 U28NR16g 8192 표본의 다중집합 부분집합(비트 동일 주장 성립); `.txt` 14행 `# SNR set     : -6 -3 0 3 6 9 12 15 dB`. 재측정은 `--tag U28NR16gR` 로 tagged 경로에 써서 동결 파일을 덮지 않는다.
- 링크·사본·sha: `ckpt → /home/HTJ/t2/conf/ckpt`, `raw_NR16B16e4`·`raw_U28B16e4`·`results/gmm_fits_D2_U28B16e4` → main; `raw_B16e4k` 448 파일·`raw_B16e4` 1344 파일(C2 448) git 추적; `gmm_fits_D2_B16e4k` 24 개 상대 링크가 추적된 `gmm_fits_D2_n16e4` 로 해소. ckpt sha256[:16] 4443921ce8d5c4a1 / c050d611b2c714a6 / 6f3a1b9490864af1, D2 C9 last 1f782042a5ad06b8 · best 3cf5d3eff96f0341 모두 문서와 일치; UMi28 1.6e5 ckpt 는 아직 없음(문서대로).
- TMXa 파일 머리말 git 09a840d7, date 2026-10-01 00:52:08 KST(= 09-30 10:52 CDT), PASS. HISNR 프로세스 cmdline 에 `code/runner.py run` 포함 → pgrep 전제가 잡는다. worktree 미커밋 코드 = 문서 ①–⑫ 목록과 일치(runner, sigma, em_batched_check_nr, testbed_mix3, frontier_ci 수정; check_frontier_scale, run_scale2.sh 신규; common.py ① 미적용). v1 integ 반드시 1·2·3·6·7·8 은 v2 문서·코드에서 해소됨(3 = score.py aborted 의미와 일치, 6 = ald.py 인자와 일치, 8 = `rs.take(base raw, k, x)` 로 base 키 재표본 + 항등 검사).
