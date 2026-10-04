# NSCALE 등록 검토 원문 — 라운드 3 (워크플로 wf_55091ec4-9d3; 작성자 Opus 5.5, 검토자 Fable 5.1 두 관점)

## 작성자 보고

Round 3 is applied to both target files, which remain uncommitted. `bash -n` passes, and every scratch harness gives the expected result. No GPU, BLER or deletion commands were used, `{{NOW}}` placeholders are kept, and no clock times were typed.

Files:
- `/home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md` (now v2)
- `/home/HTJ/t2/conf/code/run_nscale.sh`

**Header**
- Title and status bumped to v2.
- Added a round-2 row to the review table: 5 musts merged into 4; 14 of 15 shoulds applied; integ should 10 (the `prereg_reviews_nscale/` directory) is left to the main session, and that directory now exists.
- Added a bullet "2차 적대적 검토 반영 (v1 → v2)" covering each id and where it changed, the three main-session decisions, what this round opened, and the check results.

**MUSTs**
1. **r2 M1 = integ2-M1 (Q-K vs L⁰ overlap):**
   - §2.2 L⁰ item: a forced Q-K condition now comes first and writes "[K 상한 민감: 외삽 불가] (<사유>)" whatever L⁰ is. The L⁰ rule now applies only to Q-OP, and to Q-K when it is not forced. When both apply, two lines are written.
   - §2.2 Q-K (1) and the §1 Q-K row are rewritten to match, with shoulds (f) folded in: (가) the three script-forced conditions, and (나) frontier_ci's own path. I checked `cmd_recovery`: it prints the phrase on the `R<j>+` line, prints `R1+ - R2+: n/a` only when the point R⁺ is undefined (the denominator condition alone still prints a CI), and (b)(c) still run.
   - Rule written in the doc: the condition counts as forced if the phrase appears on any `R<j>+` line in that cell's Holm-level (a)(b)(c) files.
2. **r2 M2:** §2.2 S_N C2 is now decided on each new point's table-B `b* → V1` output only. Gate status is written alongside, and a gate-FAIL point is labelled "예산 축 측정".
3. **r2 M3 (lateness is not F1; S5 is single-shot):**
   - Doc: F1, the 실행 위치·커밋 row, the 실행 스크립트 row and the §4.2 schedule now say §5 is committed only when every GPU product is final or one of F1 (i)–(iv) has happened. Otherwise the CPU waits.
   - Script: the first eval start writes `<sha256(S5)> <HEAD>` to `logs/nscale/nscale_s5.start`, and the same value goes into the `start eval` log line.
   - Every later start, with or without `--resume`, aborts if either value differs. It also aborts if the marker is missing but the log already has a `start eval` line.
4. **integ2-M2:** the §5 template's B128e4 line now shows the full 14 fields. The F1 form is a separate `#` comment line saying exactly `PT B128e4 -`. A comment at the end of a PT line would break `s5()`, which is why it is on its own line. §1 F1, the §5 대체 규칙 row and the script header say the same.

**SHOULDs (a)–(m)**
- **(a) `why()`:** now gives four distinct reasons: training/fit failure, acceptance failure, `--paired` genie assert (it greps `genie differs`, so it stays "수용 실패" as the §1 guard row requires), and any other non-zero frontier_ci exit code as "정의 불가 (frontier_ci rc n)".
- **(b) §3 header:** under F1, the 1.28e6 shares of predictions are "채점하지 않음 (F1)", not misses.
- **(c) prep D1 gate:** if `samplecx.csv` has more than one row for the same N_train, prep prints all rows (with val_loss) and puts `?` in the DRAFT gate, which eval rejects. It also lists each D1 last ckpt (including `_fb<k>`) with sha256[:16] and its `# done` line. The §1 자격 row and the §5 D1 row are updated to match.
- **(d)** The (T±) parenthesis now includes "attempt 1 · 학습 집합 1 개 (공개 3·5)".
- **(e)** 공개 9 gets the sentence on the expected L⁰ = (T0) result.
- **(f)** Folded into must 1.
- **(g)** New eval preconditions:
  - `k2set`: each K2 link set must be non-empty and hold no `kronK4096_*` file.
  - K8 run 1 requires the kron 8192 merged file and a live B64e4 point.
  - `pt()` moved up next to `s5()` so this check can call it.
- **(h)** §4.1 now gives the exact `env -C` commands for the three GB′ re-runs, with logs fixed at `~/t2/conf/logs/nscale/gbp_<T>.log`.
- **(i)** The cost row now covers B64e4k8: K 8192, no `--worker-gb`, first-chunk RSS to be written in §6.
- **(j)** F5 now says `PT B64e4 -` means K8 run 0.
- **(k)** CPU cost recalibrated from SCALE16e4's finished run logs. Total goes from 6–8 h to 7.5–9.5 h (F1 saves 1.3–1.8 h).
  - UMi28 C6 A took 2 h 01 m, its chk 1130 s, its last 44 m, and K2 11 m.
  - The biggest gap is the C6 bridge: 2103 s measured, against roughly 5 min budgeted in v1 for both bridges together.
- **(l)** Unused `csv()` removed.
- **(m)** §0.5, §4.1 and §4.2 #1 now record that all three batched checks passed, with the EM-equivalence numbers and timings. Prediction 1 is marked "동결 전 확인".

**Checks** (scratch `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/nscale_reg/r3/`; every function and guard block was extracted verbatim from the script)
- **qk** (`t_qk_why.out`): the 6 cases branch the same way as in round 2.
- **why** (`t_qk_why.out`): all 6 reason paths give the expected text.
- **Single-shot** (`t_single.out`, scratch git repo, 8 cases):

| Case | Result |
|---|---|
| First start | marker written, passes |
| Resume, same S5 and HEAD | passes |
| New S5 commit | aborts (single-shot) |
| Unrelated commit | aborts (HEAD is not the §5 commit) |
| Reset back to the first S5 commit | passes |
| S5 changed then changed back (same sha, new HEAD) | aborts |
| Marker missing, log has an earlier `start eval` | aborts |
| Marker restored | passes |

- **Preconditions** (`t_pre.out`, fake tree, 7 cases):

| Case | Result |
|---|---|
| F1 + `PT B128e4 -` + template comment line + C6 `- - -` at kron 4096 + K8 1 | passes |
| `PT B128e4 C2 1280000 -` | aborts |
| Gate `?` | aborts |
| `kronK4096_` file in the K2 set | aborts |
| K8 1 with no 8192 file | aborts |
| K8 1 with `PT B64e4 -` | aborts |
| `PT B64e4 -` with K8 0 | passes |

- **prep on the two base points** (scratch mirror, `samplecx.csv` filtered to N_train ≤ 3.2e5): b*, r, c_K, K2 and the DRAFT PT lines match round 2 exactly. Only the D1 lines changed. Duplicating the 3.2e5 row prints both rows and gives gate `?`.

**Open for the main session**
- **Prediction 5 under F1:** I kept prediction 5's "F1 미발동" scored, so F1 happening counts as a miss, to stay consistent with 18 (a). Only the 1.28e6 shares of the other predictions are unscored. Please confirm that reading of your decision.
- **Q-OP overlap:** Q-OP has a similar unresolved overlap: "R* 정의 불가" versus L⁰ ≠ primary. Both outcomes are non-claims, so I left it alone.
- **Disclosure:** this round opened the three check files, the bpass listing, and the timing lines of finished SCALE16e4 and B32e4 logs. Those lines also show chunk BLER16 values for the old, already recorded runs. No new-budget BLER, NSCALE training log, checkpoint or new `samplecx.csv` row was opened.

## 검토 — 관점 stats-fair

### must
- **stats-fair r3 M1** (NEXT_EXPERIMENTS_NSCALE.md §2.2 합성 문장 S_N (C2 조건, :173) + 끝 문장 "하나라도 아니면 개수 문장만 쓴다"; 예측 8 (:214) 의 S_N 몫)
  - 문제: S_N 의 C2 점 집합이 고정되어 있지 않다. 조건은 "새 점 각각의 표 B 출력이 모두 '통과'" 이고 문장은 "N′ = 1e4 … <최대 N′> (<배수> 배) 의 등록된 모든 예산 점", 실패 시 "등록된 n 개 중 k 개" 인데, F1 (`FALLBACK 1`, `PT B128e4 -`) 이면 B128e4 에 표 B 가 없다. 읽기 A: '새 점' = S5 에 행이 있는 점 (B64e4 만) → B64e4 통과면 S_N 성립 (<최대 N′> 6.4e5, 64 배). 읽기 B: B128e4 는 등록된 새 점이고 '통과' 가 아니므로 개수 문장 ("6 개 중 5 개"). 두 읽기의 차이는 B64e4 의 BLER 을 본 뒤 전사 때 드러나므로 결과가 문장을 고른다. 반대로 F1 아닌 결손 (`PT B64e4 -` 학습 실패, A 수용 실패로 표 B 없음) 에 읽기 A 를 적용하면 측정하지 않은 6.4e5 를 포함해 "1e4 … 1.28e6 모든 점" 이라는 거짓 문장이 가능하다. §1 F1 은 1차 대비·2차·예측 채점만 정하고 S_N 은 정하지 않으며, §3 머리말의 F1 규칙 (1.28e6 몫 '채점하지 않음') 도 예측에만 적용된다. 선례 (B32e4·C6B16e4·SCALE16e4) 에 S_N 이 없어 참조로도 해소되지 않는다.
  - 수정: :173 의 "C2 — 새 점 각각의 표 B `b* → V1` 출력이 모두 '통과' (POWERED 이고 second arm fewer ≥ 2/3; **D1 게이트와 무관하게 표 B 출력으로만 판정**하고 게이트 상태는 옆에 적는다) 일 때만" 을 다음으로 교체: "C2 — **점 집합 (지금 고정; §5 의 `FALLBACK` 으로만 정해지며 BLER 과 무관)**: `FALLBACK 0` 이면 {1e4, 4e4, 1.6e5, 3.2e5, 6.4e5, 1.28e6} (n = 6, <최대 N′> = 1.28e6, <배수> = 128); `FALLBACK 1` (F1) 이면 {1e4, 4e4, 1.6e5, 3.2e5, 6.4e5} (n = 5, <최대 N′> = 6.4e5, <배수> = 64) 이고 문장 끝에 \"(F1: 1.28e6 미실행)\" 을 붙인다 — F1 은 BLER 전 §5 에 고정되는 사실이라 집합을 줄이는 것은 결과 뒤 선택이 아니다 (§3 머리말의 F1 채점 규칙과 같은 취급). **F1 이 아닌 결손은 집합에서 빼지 않는다**: `PT B64e4 -` (학습·적합 실패), A 수용 실패로 표 B 가 없는 점, '통과 못함' 은 모두 '통과 아님' 이다. 그 집합의 새 점 각각의 표 B `b* → V1` 출력이 모두 '통과' (POWERED 이고 second arm fewer ≥ 2/3; **D1 게이트와 무관하게 표 B 출력으로만 판정**하고 게이트 상태는 옆에 적는다) 일 때만". 같은 항목 끝의 "하나라도 아니면 개수 문장만 쓴다 (\"등록된 n 개 예산 점 중 k 개에서 (i)\")" 를 "하나라도 아니면 개수 문장만 쓴다 (\"위 집합 n 개 예산 점 중 k 개에서 (i)\"; n 은 위 집합 크기 = `FALLBACK 0` 6 / `FALLBACK 1` 5, k 는 표 B '통과' 인 점 수)" 로 교체. 예측 8 (:214) 끝에 "(F1 이면 S_N 은 5 점 집합으로 채점)" 을 덧붙인다.

### should
- §2.2 Q-OP (:170): "어느 끝이든 R\* 정의 불가면" 을 SCALE16e4 §1 Q-OP 정의·`frontier_ci.py` 출력 (`cmd_rstar`: und > 0.05 또는 점추정 정의 불가면 `R*<j>` 줄 끝 '[운영점 한정어 정의 불가]') 과 같게 명시하고 L⁰ 규칙보다 앞세울 것: "어느 끝이든 R\* 점추정이 정의 불가이거나 정의 불가 복제 > 5 % (`R*<j>` 줄 끝의 '[운영점 한정어 정의 불가]', 또는 `R*1 - R*2: n/a`) 이면 L⁰ 와 무관하게 \"[운영점 한정어 정의 불가]\" 만 쓴다 (Q-K 강제와 같은 우선 규칙; 그때 `R*1 - R*2` CI 는 보고 전용). 그 밖에 L⁰ ≠ 1차 라벨이면 '[한정어 판정 불가 …]', 그 밖에 L\* CI 가 …" — 지금은 점추정만 정의되고 복제 6 % 가 정의 불가인 경우 CI 로 '강건' 을 쓰는 읽기가 남는다 (§1 의 'SCALE16e4 정의 그대로' 참조로만 막힘).
- run_nscale.sh:252 뒤에 `[[ "$K8RUN" =~ ^[01]$ ]] || die "$S5: K8 line missing or run not 0|1"` 추가 — 지금은 `K8` 줄이 없으면 K8RUN 이 빈 문자열이라 조용히 run 0 으로 돈다 (S5 는 BLER 전이라 라벨 문제는 아니지만 §5 틀의 필수 줄이 빠진 채 시작된다).
- `prep` `done()` (run_nscale.sh:94–98) 은 마지막 `# done` 줄을 쓰는데, §4.1 GB′ 재실행 (`run_d2_sx.py`/`train_nr16.py` 를 `--no-gbprime` 없이) 은 `score.train` 의 '이미 정지' 재개 경로 (:954–957 `# resume … no epoch trained`, 그 뒤 :1036 `# done` 을 다시 씀; wall ≈ 0 s, ep − ep0 = 0) 로 두 번째 `# done` 을 남긴다 → §5 체크포인트 행의 '초' 와 보고 전용 '학습 초' 가 재실행본 값으로 잘못 전사된다. `done()` 이 첫 `# done` (또는 전부) 을 출력하게 하고 §5 행에 "첫 `# done` 줄" 로 적을 것.
- §1 자격 행 '?' 해소 규칙에 한 구절: "같은 ckpt 의 재측정 행은 GA–GD 가 동일하다 (`gates_D1` 은 stream 10 + `SEED_GATE` 로 결정적) — 값이 다른 행은 다른 ckpt·epoch 의 행이다" — '?' 해소가 값을 고르는 일이 아님을 명시.
- §1 F1 (ii) "재시작 하나라도 CUDA OOM" 과 (iv) "같은 시드 재실행 1 회 뒤에도" 가 비대칭이다. (ii) 에 "(OOM 은 재실행하지 않는다 — Exclusive_Process·같은 n·K 라 결정적)" 을 덧붙여 한 읽기로 고정 (BLER 전 결정이라 must 아님).

### verified
- 2차 반드시 4 건 반영 확인: r2 M1 = integ2-M1 → §2.2 L⁰ 항목 끝 문장·Q-K (1) (:169, :171), §1 Q-K 행 (가)/(나) (:119) 가 `frontier_ci.py cmd_recovery` 와 맞음 (:245 r ≥ 1 문구, :250 `und = mean(~(fpg > 0))` 끝 j 별 ΣF⁺ ≤ ΣF_g 비율 > 0.05 또는 R⁺ 비유한 → `R<j>+` 줄 끝 '[K 상한 민감: 외삽 불가]', :257/:260 `R1+ - R2+` CI 또는 `n/a (Q-K undefined)`; (b) `--extrap <K2_새> -` 는 k2[1] = None → bp = bo 로 `R1+ - R2+` 를 찍음); r2 M2 → :173 표 B 출력 기준 문장; r2 M3 → §1 F1 (:113) '미완료는 F1 사유가 아니다', 실행 위치·커밋 (:123), 스크립트 :215 (HEAD = S5 마지막 커밋) · :216–218 (`nscale_s5.start` = `sha256(S5) HEAD` 대조, 표시 파일 없음 + 로그 `] start eval` → ABORT) · :259–260 (첫 시작 때 쓰기, 로그 줄에 같은 값); integ2-M2 → §5 틀 :281–283 (14 필드 B128e4 줄 + 별도 주석 줄 'PT B128e4 -'), §1 F1 '(정확히 이 두 필드 형식)'.
- 스크래치 하네스 재독 (`nscale_reg/r3/`): `t_single.out` 8 경우 (첫 시작 PASS·같은 S5/HEAD 재개 PASS·새 S5 커밋 ABORT·무관 커밋 ABORT (HEAD ≠ S5 커밋)·되돌림 PASS·S5 같고 HEAD 다름 ABORT·표시 파일 없음+로그 ABORT·복원 PASS), `t_pre.out` 7 경우 (정상 PASS, `PT B128e4 C2 1280000 -` ABORT, gate '?' ABORT, K2 집합 `kronK4096_` ABORT, K8 1 + 8192 없음 ABORT, K8 1 + `PT B64e4 -` ABORT, `PT B64e4 -` + K8 0 PASS), `t_qk_why.out` (qk 6 분기·why 6 사유) 가 스크립트 본문 (:216–218, :222–224, :231–254, :410–414, :447–461) 과 글자대로 같고 문서 규칙과 일치.
- 단일 S5 의 우회 분석: 표시 파일·`run_nscale.log` (둘 다 미추적) 를 지우고 새 §5 를 커밋해 `--resume` 해도 `H` 가 바뀌어 수용 (f) `gitchk` (:273–287, 모든 청크 `run|git == H`) 가 옛 raw 를 전부 FAIL 시키므로 (P2 → (T-iv) 수용 실패) 결과를 본 raw 를 새 S5 아래서 재사용할 수 없다 — 규칙이 두 독립 검사로 막힘.
- `bash -n code/run_nscale.sh` 통과; 두 대상 파일과 `results/review_next/prereg_reviews_nscale/` 는 `??` (미추적, 커밋 없음).
- `frontier_ci.py --recovery raw_B32e4:C2:-3,0,3 raw_B16e4k:C2:-3,0,3 --rstar 0.05 --level 0.95 --B 20` (기록된 기준 raw, 단일 프로세스, nice 19) rc 0: `R1 - R2 … (--level 0.95)` 줄과 `R*1 - R*2` 줄이 찍힘 → 강제 모드의 실행 (a) (`--extrap` 없이 `--rstar` 만) 이 유효하고 L⁰ 줄이 존재.
- §0.5 일괄 검사 수치가 세 파일과 줄 단위로 일치 (`results/nr8b_batched_check_S2_n640000.txt`·`_n1280000.txt`·`nr16b_…_n640000.txt` :10–14): (a) max|dll_t| 8.70e-13 / 1.92e-13 / 2.63e-12, rel dcov 6.66e-12 / 4.25e-12 / 2.19e-12, |dpi| 1.28e-14 / 1.07e-14 / 8.64e-15, 재시드 0/0; (b) 255/255 · 255/255 · 371/371; kron 2048 14.1 / 28.6 / 49.1 s/iter; `VERDICT: PASS` ×3; `logs/nscale/bpass_nr8_n640000`·`bpass_nr8_n1280000`·`bpass_nr16_n640000` 존재 (0 바이트). 파일에 BLER 없음.
- §4.1 GB′ 재실행 명령: `run_d2_sx.py --tag` (fits 디렉터리 태그, :39 → `runner._init`) 와 `train_nr16.py --fits-tag` (:46) 존재, 둘 다 `GMM b* = … @N=` 을 찍어 (:88, :83) `prep` 의 grep (:148) 과 맞음; `score.train(resume=True)` 는 정지 규칙을 이미 만족한 ckpt 를 건드리지 않음 (:847, :954–957) → 재실행이 `_best.pt`/last sha 를 바꾸지 않음 (단, 두 번째 `# done` 줄은 남김 — should 3).
- D1 게이트: `run_samplecx.py` 가 `ckpt/sx_N{N}_D1{sfx}.pt`·`logs/train_sx_N{N}_D1{sfx}.log` 를 쓰고 (:22–24) last 파일을 `gates_D1(…, stream=10)` 으로 재며 (:29), `gates_D1` 은 `train_rng("D1", prior, Nr, 10)` + `default_rng(SEED_GATE)` 로 결정적 (score.py:1258+) → `prep` 의 glob `ckpt/sx_N{n}_D1*.pt`·`done()` 이름과 일치, 같은 ckpt 의 중복 행은 동일 값.
- 주 세션 결정 3 건 (Q-K 강제 우선·늦음은 F1 아님+단일 S5·F1 때 예측 미채점) 의 구현 문안은 다시 제기할 결함 없음; 예측 5 'F1 미발동' 채점 유지는 §3 머리말 끝 문장과 18 (a) 와 일관.

## 검토 — 관점 integ

### must
- **integ3-M1** (run_nscale.sh:94-98 (`prep` `done()`) · NEXT_EXPERIMENTS_NSCALE.md §5 '체크포인트' 행 (:264) · §1 보고 전용 행 '학습 초·epoch' (:121) · §1 수용 (c) (:122))
  - 문제: `prep` 의 `done()` 은 학습 로그의 **마지막** `# done` 줄을 §5 용으로 내놓는데, 등록 순서 (GB′ 재실행 → `prep` → §5) 에서는 그 마지막 줄이 학습이 아니라 GB′ 재실행의 재개 줄이다. `score.train` 은 끝난 체크포인트를 재개하면 `# resume … no epoch trained, … left untouched` 뒤에 **새 `# done` 줄을 wall = 재개 시간으로** 다시 쓴다 (score.py:955-958, 1035-1037: `wall / max(ep - ep0, 1)` = wall/1). 실증: `logs/train_d2sx_N320000_a1.log` :994 `# done : 986 epochs … wall 40953.8 s, 41.535 s/epoch` (학습) 와 :1002-1003 `# resume … no epoch trained` + `# done : 986 epochs … wall 3.3 s, 3.278 s/epoch` (B32e4 GB′ 재실행); 드래프터의 `prep` 기준점 출력 (`r3/t_prep_r3_single.txt`) 도 B32e4 에 `wall 3.3 s, 3.278 s/epoch` 를 보인다. §5 '체크포인트' 행은 `# done` 줄의 '초' 를, §1 보고 전용은 '학습 초·epoch' 를 기록 항목으로 두므로 새 세 점의 학습 시간이 3 s 대로 오기록된다 (stopped_by·aborted·epoch·best val 은 체크포인트 값이라 맞다). 체크포인트 sha 는 영향 없다 (`left untouched`, 저장은 루프 안에서만).
  - 수정: run_nscale.sh:94-98 을 다음으로 교체:
def done(stem):                                 # EVERY '# done' / '# resume' line: the FIRST '# done' is the training; a later
    lg = f"logs/train_{stem}.log"               # pair '# resume ... no epoch trained' + '# done' is a GB' re-run's resume (its wall = the resume's)
    l = [x.strip() for x in open(lg)] if os.path.exists(lg) else []
    d = [x for x in l if x.startswith("# done") or x.startswith("# resume")]
    return " || ".join(d) if d else f"(no '# done' line in {lg})"
문서 §5 '체크포인트' 행 (:264) 의 "`# done` 줄 (stopped_by·aborted·epoch·초)" 를 "`# done`·`# resume` 줄 전부 (`prep` 출력 그대로); **첫 `# done` 줄 = 학습** (stopped_by·aborted·epoch·초는 여기서만), 그 뒤의 `# resume … no epoch trained` + `# done` 은 GB′ 재실행의 재개라 wall 이 재개 시간이다 (score.py 재개 규칙; B32e4 로그 :994 대 :1003)" 로 교체. §1 보고 전용 행 (:121) 의 "학습 초·epoch" 를 "학습 초·epoch (첫 `# done` 줄)" 로, §1 수용 (c) (:122) 의 "학습 로그 `# done` 줄 (stopped_by·aborted) 을 출력" 을 "학습 로그의 `# done`·`# resume` 줄 전부를 출력 (첫 `# done` = 학습; GB′ 재실행은 no-epoch 재개 쌍을 더한다)" 로 교체.

### should
- run_nscale.sh:252 뒤에 `[[ $K8RUN =~ ^[01]$ ]] || die "$S5: K8 line missing or run not 0|1"` 한 줄: S5 에 `K8` 줄이 없으면 `K8RUN` 이 빈 값이 되어 조용히 run 0 으로 돈다 (내 하네스 case b: PASS, `K8RUN ''`). 틀은 줄을 요구하므로 빠진 줄은 전제 ABORT 가 맞다.
- run_nscale.sh:148 `prep` 의 GB′ 로그 줄 grep: `logs/nscale/*.log` 전체에서 `@N={n}` 으로 고르면 B64e4 와 NR16B64e4 가 같은 `@N=640000` 이라 서로의 `[d2sx]`/`[nr16]` 줄이 두 블록에 함께 찍힌다 (train_nr16.py:83 도 `GMM b* = … @N=`). 로그 경로가 §4.1 에 `gbp_<T>.log` 로 고정됐으니 `glob.glob(f"logs/nscale/gbp_{T}.log")` 만 읽을 것.
- 단일 S5 의 승인 경로 (§1 실행 위치·커밋 행 '새 §5 는 사용자 승인 + DECISIONS') 에 절차가 없다: 표시 파일이 있거나 로그에 `start eval` 이 있으면 스크립트는 영원히 ABORT 한다. 한 문장 추가: "승인된 새 §5 는 주 세션이 `logs/nscale/nscale_s5.start` 와 `logs/run_nscale.log` 를 `*.1` 로 **옮기고** (삭제 아님; 이전 실행의 raw 는 `--resume` 없이 ABORT 하므로 그 raw 도 `raw_<T>.1` 로 옮긴다) DECISIONS 줄 뒤 시작한다" — 현 스크립트에서 바로 통한다 (로그 없음 → 표시 파일 없음 OK).
- §1 실행 위치·커밋 행에 커밋 절차 한 문장 (SCALE16e4 :411, Fable M1 선례): "§5 커밋은 명시 경로로만 (`git add results/nscale/nscale_s5.txt results/nscale/nscale_prep.txt results/review_next/NEXT_EXPERIMENTS_NSCALE.md DECISIONS.md`); `git add -A`·`git add results` 금지" — `git check-ignore` 가 `results/gmm_fits_D2_K2B32e4`·`raw_K2B32e4`·`logs/nscale/nscale_s5.start` 모두에 빈 출력 = 무시 규칙 밖이라 `-A` 는 링크 집합·GB 단위 fits 를 커밋에 넣는다.
- §1 실행 위치·커밋 행: DECISIONS 의 §5 (실행) 줄은 **같은 §5 커밋**에 넣는다고 적을 것 — 뒤에 따로 커밋하면 :215 `HEAD = S5 마지막 커밋` 전제가 ABORT 한다 (내 하네스 case 7). 또 SCALE16e4 §4.1 (:265) 의 "실행 중 (`NSCALE_DONE` 전) 이 문서와 DECISIONS.md 를 편집하지 않는다 — `--resume` 도 :214 추적·청결을 요구" 문장을 §4.1 `eval` 행에 옮겨 적을 것.
- run_nscale.sh:359-360, 396-397: c_K = inf (r ≥ 1) 인데 K2 가 구성 가능하면 `K2<T>` BLER (192 파일) 와 그 수용을 돌리고도 `qk` 가 강제 한정어로 외삽을 생략한다 — 결과에 영향 없는 비용 (~5–10 분) 이라 그대로 두어도 되나, 머리말에 '강제 조건이어도 K2 raw 는 보고 전용으로 남긴다' 한 구절을 적으면 §6 전사가 헷갈리지 않는다.

### verified
- 라운드 2 반드시 4 건이 문안·코드에 들어 있음: (M1=integ2-M1) §2.2 L⁰ 항목 끝 문장·Q-K (1)·§1 Q-K 행이 '강제 조건 우선, L⁰ 규칙은 Q-OP (와 강제 아닌 Q-K)' 로 일관; `frontier_ci.py cmd_recovery` (:243-262) 는 `R<j>+` 줄 끝에 `[K 상한 민감: 외삽 불가]` 를 (r ≥ 1 / 분모 ≤ 0 복제 > 5 % / 점 R⁺ 비유한) 에 찍고, 점 R⁺ 비유한일 때만 `R1+ - R2+: n/a (Q-K undefined)`, 아니면 CI 를 찍는다 = 문서 (나) 서술. (M2) §2.2 S_N C2 조건 = 표 B 출력만. (M3) §1 F1 '늦음은 사유 아님' + 단일 S5: 스크립트 :215-218 (HEAD = S5 마지막 커밋, 표시 파일 `logs/nscale/nscale_s5.start` = 'sha256(S5) HEAD' 대조, 표시 파일 없이 로그에 `] start eval` 이면 ABORT) 와 :259-260 (첫 시작 때 쓰기, 같은 값을 `start eval` 줄에). (integ2-M2) §5 틀 B128e4 줄 14 필드 + 별도 `#` 주석 줄 'PT B128e4 -'; `s5()` 는 `$1=="PT"` 만 읽어 주석 줄을 무시한다.
- 단일 S5 하네스 (스크래치 git 저장소 `nscale_reg/fable3/ssrepo`, :215-218·:259-260·:34 `log` 그대로 추출): 첫 시작 → 표시 파일 생성 PASS; 같은 S5·HEAD 재개 PASS; 표시 파일 0 바이트 + 로그 `start eval` → ABORT; 표시 파일 없음 + 로그 → ABORT; 표시 파일 복원 → PASS; FALLBACK 을 바꾼 새 S5 커밋 → ABORT (single-shot); 무관한 커밋 → ABORT (:215 HEAD ≠ S5 커밋); 되돌림 → PASS; 로그 없음 + 표시 파일 → PASS. (처음 내 스텁 `log` 가 `]` 없는 형식이라 두 경우가 거짓 PASS 였고, 실제 `log()` 형식으로 재실행해 ABORT 확인 — 스크립트 결함 아님.)
- S5 전제 하네스 (`fable3/pre`, :49-50·:219·:222-224·:231-232·:236-254 그대로 추출, 가짜 ckpt sha·링크·K2/K8 파일, 17 경우): 정상 FB 0 (K2 2048·c_K 1.5·K8 `- - 0`) PASS; PT 중복 줄 → 28 필드 ABORT; PT 줄 끝 주석 → 16 필드 ABORT; c_K 0.99 → ABORT, c_K 1·inf → PASS; FALLBACK 0 + `PT B128e4 -` → ABORT; FALLBACK 1 + B128e4 줄 없음 → ABORT; FALLBACK 0 + B128e4 줄 없음 → 14 필드 (has 0) ABORT; C2 gate UNGATED / C6 gate PASS → ABORT; b* = gmm512 (kron_K '-', `- - -`) → PASS (내부); b* = kron 2048 인데 K2 채움 → ABORT; FB 1 + `PT B64e4 -` + `PT B128e4 -` + K8 0 → PASS (C2PTS 빈 집합); K8 `8192 ll 1` + 파일 + B64e4 → PASS, K8K 4096 + run 1 → ABORT; `_fb2` stem 은 그 파일의 sha 로 검사; sha 불일치 → ABORT. K8 줄 없음 → PASS (권고 1).
- `links` 하네스 (`fable3/lk`, :180-193 그대로): `lset K2B64e4 B64e4 'kronK4096_'` → 20 링크 (후보 6, kron 4096 계열 0), 두 번째 실행 무변경; `lset B64e4k8 B64e4 '' gmm_fits_D2_K8B64e4/fit_S2_Nr8_kronK8192_n640000.npz` → 25 링크 (B64e4 24 전부 + 8192 병합 1, 8192 후보 0, kron 4096 병합 포함 = 설계대로 B64e4 격자 + 8192); 다른 곳을 가리키는 기존 링크 → ABORT, 교체 없음; `k2set` 은 kron4096 없는 K2 집합 OK, 8192 집합·없는 집합 ABORT.
- `qk`·`why`·`ok`·`pt` 추출본이 드래프터의 `r3/qk_fn.sh`·`okpt_fn.sh` 와 바이트 동일 (diff) 이고 `r3/t_qk_why.out` 의 6+6 경우가 §1 Q-K (가) 세 강제 조건·(a)(b)(c) 인자·`why` 네 사유와 일치; `frontier_ci.py` 의 genie assert 문구는 `genie differs` (:172 `--recovery`, :312 `--paired`) 라 `why` 의 grep 과 맞다.
- 플래그 전부 argparse 에 존재: eval_accept (`--tag --ntrain --kron-K --ll-val --n --points --ref-raw --ref-arms --fits-dir --grid --cand-dir --nr --prior --bstar`; `--nr` 는 `--grid` 파일명에만 쓰여 chk/last/bridge 호출에 `--nr` 이 없어도 무해, `--bstar` 는 'kron' 또는 'gmm<K>' = prep 의 b 값), frontier_ci (`--pair --recovery --paired --level --extrap --ck --rstar`), recovery_ci (`--raw --cell --snrs`), guard_report (`--raw --testbed`), run_manifest (`--tag`), runner (`run|analysis`, `--testbed --prior --cell --snr --n --chunk --arm --ntrain --stagec-ckpt --tag`); §4.1 GB′ 명령의 `run_d2_sx.py --tag/--fallback/--ntrain`·`train_nr16.py --nr/--ntrain/--fits-tag` 존재 (train_nr16.py:52,74 가 `gmm_fits_D2_<fits-tag>` 를 읽음) 이고 주 세션의 `logs/nscale/gbp_watch.sh` 가 같은 명령·같은 로그 경로 `gbp_<T>.log` 로 큐에 넣는다.
- 이름 일치 (run_nscale_gpu.sh ↔ run_nscale.sh ↔ 코드): fits `results/gmm_fits_D2_{B64e4,B128e4,NR16B64e4,K8B64e4}/fit_S2_Nr<nr>_<fam>K<K>_n<N>.npz` (+ `.k0r<r>.npz` 후보; prep `grid()` 정규식은 병합만), 검사 파일 `results/nr{8,16}b_batched_check_S2_n<N>.txt`·`logs/nscale/bpass_nr<Nr>_n<N>`, 적합 로그 `logs/nscale/fit_<T>_*.log` (K8 는 `fit_K8B64e4_*` 라 B64e4 glob 에 안 걸림), 학습 stem `d2sx_N640000_a1`·`d2sx_N1280000_a1`·`d2sx_NR16_N640000_a1` (run_d2_sx.py:63-67, train_nr16.py:54-58; `_fb<k>` 접미 규칙 동일), 로그 `logs/train_<stem>.log`, D1 `ckpt/sx_N<N>_D1[_fb<k>].pt`·`logs/train_sx_N<N>_D1[_fb<k>].log` (run_samplecx.py:22-24) = prep 의 경로. `arms.load_fits` 는 있는 파일만 읽어 (arms.py:72-82) 8192 가 없는 디렉터리도 정상이고 `D2_KS` 의 8192 (b212d683, B32e4 이전) 는 `gmm_fits_D2_B64e4k8` 집합에서만 선택에 들어간다.
- §0.5 의 일괄 검사 수치가 세 파일과 일치 (열람: `results/nr8b_batched_check_S2_n640000.txt`, `…_n1280000.txt`, `nr16b_batched_check_S2_n640000.txt`; EM 동등성·시간만, BLER 없음): (a) max|Δll_t| 8.70e-13 / 1.92e-13 / 2.63e-12, rel dcov 6.66e-12 / 4.25e-12 / 2.19e-12, max|Δπ| 1.28e-14 / 1.07e-14 / 8.64e-15, 재시드 0/0; (b) 255/255 · 255/255 · 371/371; kron 2048 일괄 14.1 / 28.6 / 49.1 s/iter; 세 `VERDICT: PASS`, `bpass_*` 세 파일 (0 바이트) 존재. §0.4 의 B32e4·NR16B16e4 ll_val·r·c_K·재시드·경로·정지 사유가 드래프터 prep 출력 (`r3/t_prep_r3_single.txt`) 과 일치하고, 복제 행 변형 (`t_prep_r3_multi.txt`) 은 두 행 + gate '?' 를 낸다.
- 재개 안전성: `run()` 은 완성 raw 를 건너뛰고 호출마다 HEAD 불변 검사, runner 는 끝난 청크를 건너뜀; 후처리 출력은 `>` 덮어쓰기라 재실행 결정적; `--resume` 은 같은 S5·HEAD 에서만 (단일 S5). `score.train` 재개는 끝난 체크포인트를 건드리지 않아 (`left untouched`, 저장은 epoch 루프 안) GB′ 재실행 뒤에도 sha 불변 — 다만 `# done` 줄이 하나 더 생긴다 (반드시 1). `exit $((FAIL > 0))`, `NSCALE_DONE ok= fail=` 끝 표시, flock, `pgrep -f 'code/runner.py run'`, `CUDA_VISIBLE_DEVICES=` 비움 = 문서 §1 실행 위치·커밋·실행 스크립트 행.
- 읽지 않은 것: NSCALE 학습 로그 (`logs/nscale/v1_*.log`, `logs/train_d2sx_N640000_a1.log` 등)·새 체크포인트 내용·새 fits 디렉터리 내용·`samplecx.csv` 행 (머리말만)·`~/t2_wtS` 의 어떤 파일 (SEEDSNR 포함) 도 열지 않았다; `ckpt/`·`results/gmm_fits_D2_*` 는 파일명 목록만 봤다 (1.28e6 ckpt 와 B64e4/B128e4 fits 디렉터리가 존재함을 안다, 내용 모름). 기준점 로그 `logs/train_{d2sx_N320000_a1,sx_N320000_D1,d2sx_NR16_N160000_a1_fb2}.log` 는 `# done`·`# resume` 줄만 grep. GPU·BLER·커밋·삭제 없음; 스크래치는 `nscale_reg/fable3/` 에 그대로 둔다.

