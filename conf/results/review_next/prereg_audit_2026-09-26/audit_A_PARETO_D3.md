# 기록 감사 A — Pareto (PARB16e4) · D3 (D3B16e4)  (Fable 5.1, 기록 감사 A; 2026-09-26 19:53 CDT)

대상: `NEXT_EXPERIMENTS_PARETO.md` §6, `NEXT_EXPERIMENTS_D3B16e4.md` §6, `docs/EXPERIMENTS.md` 행 2건(00:42~01:58 KST, 01:58~03:10 KST), `DECISIONS.md` 항목 2건(02:12 KST, 03:31 KST).
대조 원본: `prereg_audit_2026-09-26/recompute.out` (raw npz·ckpt·fits·csv·git 만 읽는 독립 재구현), `results/tables_D2_{PARB16e4,D3B16e4,D3B16e4last}.txt`, `results/review_next/{frontier_PARB16e4.txt, recovery_*.txt, recovery_diff_D3B16e4.txt, *_accept.txt, run_manifest_*.json}`, `results/guard_D2_{PARB16e4,D3B16e4}.txt`, `logs/run_pareto_eval.log`, `logs/run_prior_eval_D3B16e4.log`. 문서는 고치지 않았다.

## 총평
수치·판정은 **전부 재현**됐다(아래 "일치 확인" 참조). 독립 재구현(부호검정 p 는 scipy binomtest, 부트스트랩은 등록된 시드·복원추출 순서를 정의대로 다시 씀)과 analysis/recovery_ci/frontier_ci 출력이 소수점 표기 자리까지 같다 — 시드·순서가 같으므로 동일 난수열이며 재현이지 우연의 일치가 아니다. 판정 라벨·Holm 순서·포화 가드·판독표 칸·E1/E2 채점·예측 채점은 등록 규칙을 다시 적용해도 같다. 정정은 **기록 위생 4건**(수치·판정 변경 없음).

## NEXT_EXPERIMENTS_PARETO.md §6

1. [정정 필요(위생)] §6 머리말 끝 "C8 0.35–…" 와 §6.3 "V0: 가드 발동률 … C8 0.35–…(−3 dB 0.50)" — 줄임표가 값 자리에 남아 있다. `guard_D2_PARB16e4.txt` C8 발동률은 0.353(−6) ~ 0.952(+6) → **"C8 0.35–0.95"** 로.
2. [정정 필요(위생)] §6.4 항목 4 "(genie 는 Tp 에 거의 무관: C2 −4.81)" 과 EXPERIMENTS 행 메모 "genie 는 Tp 에 거의 무관" — 결과 절에 허용된 것은 라벨·수치·채점이다. 수치로 바꿔 적을 것: **"genie SNR@0.1 C2/C7/C8 = −4.81 / −4.84 / −5.26 dB (비짝 Δ C2−C7 +0.02 [−0.17, +0.22], p 0.87)"**.
3. [메모] §6 머리말에 작성 모델 표기가 없다(D3·SV·38901 §6 은 "Opus 5.5 — 전사만" 명시). DECISIONS 02:12 KST 항목은 "(Fable; …)" — 머리말에 "Fable 5.1 — 전사만, 해석 없음" 을 붙이면 네 문서가 같은 형식이 된다.
4. [메모] F3 (Eb/N0) 값은 소수 둘째 자리로 반올림된 SNR@0.1 에 상수를 더한 것(예: −2.23 + 1.829 = −0.401 → −0.40). 재계산해도 12 값 모두 같은 자리에서 일치하나, 정의상 "2 자리 반올림 값 + 상수" 임을 괄호로 적어 두면 감사 재현이 쉽다(선택).
5. [메모] 회귀 검사 재현: `raw_PARB16e4chk` 의 항목 16개(14 arm + load_raw 별칭 `R0-pilot (@1)`, `pilot_C (@16)`) × KEYS_RAW 전부가 `raw_B16e4k` C2 −3 dB 시행 0..39 와 비트 동일(recompute.out "differing []") — 문서의 "14 arm" 서술과 일치(별칭은 파생값).
6. [메모] C2 −6 dB 점의 표 B 블록(`tables_D2_PARB16e4.txt` 689행 이후)은 판정점 1개(−6)로 UNDECIDED 이고 502:57 이 찍혀 있다 — §1 (e) 가 미리 적은 대로 판정에 쓰지 않았고 §6 도 인용하지 않았다(정상).

## NEXT_EXPERIMENTS_D3B16e4.md §6

1. [정정 필요(위생)] §6.3 "D2 C2: b\* −0.81, V1 −2.23, **genie −4.81**" — genie −4.81 은 `raw_B16e4k` 7 점 격자에서는 `n/a (<= -3)` 이고, Pareto 의 C2 −6 dB 점을 합친 8 점 곡선(recompute.out "C2 (8 pts)") 에서만 나온다. 출처를 붙일 것: **"genie −4.81 (raw_B16e4k + PARB16e4 C2 −6 의 8 점 곡선; 7 점만으로는 격자 아래)"**. §0 표의 "genie ≤ −3" 와도 이렇게 맞춘다.
2. [메모] §6.4 항목 4 "V1 1000 ∈ [450, 1000] ✓" — 상한과 정확히 같은 값이다. §3 문구 "450~1000" 을 닫힌 구간으로 읽은 것이며 그대로 두어도 되나, "(경계값)" 을 병기하면 채점 해석 시비가 없다.
3. [메모] 두 태그 em_sec 15862.749816656113 동일(recompute.out); §6 의 "두 태그 em_sec 동일" 과 일치. §6 에 값 자체는 없다(선택: 기입).
4. [메모] §6 머리말 "manifest (git 07a8935a)" — 두 manifest 모두 07a8935a, config_hash 80f03e30d676712a 로 확인. `conf/code` 는 eee1d669 와 diff 없음(recompute.out §0).

## docs/EXPERIMENTS.md (행 40, 41)
- 행 40 메모 "genie 는 Tp 에 거의 무관" → 위 Pareto-2 와 같이 수치로(정정 필요(위생)).
- 그 밖의 수치(시각 KST/CDT 환산, 실행 시간 4/65/5 분·35/36 분, a:b·pooled·격차·P-a/P-b·SNR@0.1·회수율·ΔR·BLER·best 대 last·ACCEPT) 는 §6·원본과 모두 일치. §6 과 모순되는 곳 없음.

## DECISIONS.md (02:12 KST Pareto, 03:31 KST D3)
- 모순 없음. Pareto 항목의 "goodput 포락선은 −3 dB 이상 C2, −6 dB V1 은 C7·b* 는 C8, −9 dB C8" 은 frontier 파일과 일치. D3 항목의 포화 가드·판독표·2차 ΔR 값 일치.

## 규칙 적용 재검(등록 §1·§2 를 재계산값에 다시 적용)
- Pareto (A): C7 POWERED, wy=3 → (i); C8 POWERED, wy=3 → (i). 라벨 문자열은 §2 (A) 원문과 같다. 대조군 C7 (iii) 무방향, C8 first fewer 2/3 — §6 서술과 같다.
- Pareto (B): 부트스트랩 p P-a 0.0040 < P-b 0.0070 → 첫째 P-a → 95% CI [−0.67, −0.13] 0 배제 → 유의; P-b 90% [+0.14, +0.63] 0 배제 → 유의. censored 0% ≤ 10%. 라벨 문자열 §2 (B) 원문과 같다. Holm 예측 채점(첫째 = P-b 예측 → 빗나감) 맞다.
- D3: POWERED, wy=3 → (i); 포화 가드: b* BLER@16 −3 dB 0.507 ∈ [0.005, 0.9], b* 1298 > genie 485, undefined 0 → 가드 미발동; ΔR −0.104 [−0.156, −0.049] < 0 → "D3 의 회수율이 D2 보다 낮다"; 판독표 (i) & Δ<0 칸의 문장·[E2 적중·E1 빗나감] 이 §1 원문과 같고 교란 요인 3가지가 함께 적혀 있다.
- §6.4 예측 채점: Pareto 10 항목·D3 8 항목을 §3 문구 그대로 다시 매겨 전부 같은 결과(Pareto 1: 4 안/2 밖, 3: P-a ✗·P-b ✓·Holm ✗, 4: 3 ✗ + 1 ✓, 5: 3 ✗ + 2 ✓, 6: 3 ✓ + 1 ✗, 8: C7 ✗·C8 ✓·V0 ✗·V4 ✓, 9: C7 ✓·C8 ✗; D3 4: genie ✗·b* ✓·V1 ✓, 5: R ✓·ΔR ✗, 6: 대조군 ✓·V0 ✗·V4 ✓, 7 ✓).

## 일치 확인한 항목 (전수)
- 체크포인트 sha·epoch 3개(4443921ce8d5c4a1 @1784/1764; 7ebf4e6647d4413f @494; 9fc82e075a5eaf8f @514) ✓; b* ll_val 2개(−11.459169831224418, 0.08879931165293979)·em_sec 107957.18832826614 ✓; raw meta(ntrain·bstar·kron_K·ll_val·ckpt id·iters·em_sec) PARB16e4 576+64 파일·chk 1 파일·D3 448×2 파일 ✓; 청크 계획/점 집합(19 점, 7 점) ✓.
- 표 B: Pareto C7·C8 (b*→V1, b*→scalar) 각 3 점 a:b·p·pooled·가드 24 값 ✓; D3 best·last (b*→V1, b*→scalar, R2→b*) 36 값 ✓. 짝 격차 CI 8개 ✓.
- SNR@0.1: Pareto 3 셀 × 9 arm 27 값(V0 'hi' 포함) ✓; D3 best 9 값 + last V1 ✓. F3·P-c 14 값(반올림 합산) ✓.
- 비짝 부트스트랩: P-a·P-b(점추정·90%·95%·p·censored) ✓, 보고 전용 6 쌍 ✓; ΔR D3 best·last·2차 3개 ✓.
- 회수율: Pareto C7·C8 (−3, 판정점 합) 4개 + 실패 수 ✓; D3 best·last (−3, 판정점 합, 점별 3개) ✓; D2 참조 0.470/0.509 ✓.
- BLER@16 표: Pareto C7·C8 4 arm × 4 SNR + +15 dB 4 값 + C2 −6 6 값 = 42 값 ✓; D3 9 arm × 4 SNR = 36 값 + D2 3 값 ✓. goodput 포락선 16 값 ✓. V0 가드 발동률(Pareto 19 점, D3 7 점)·V0 BLER ✓. best 대 last V1 (D3 4 점 + pooled) ✓.
- 시각(CDT 로그 스탬프 12개)·KST 환산·git 해시(2b03df55, 07a8935a)·config_hash·raw 파일 수(1216, 448)·"conf/code = eee1d669" (diff 없음)·비-Stage-C 10 arm 비트 동일·C2 −6 genie 비트 동일·회귀 검사 ✓.
- 금지어(여지·headroom·bound·도달·최적·비긴다)·시각 자리표시: 두 §6·두 행·두 항목에 없음.
