# 적대적 검토 — NEXT_EXPERIMENTS_DMCBASE16e4.md v1 (DeepMIMO prior DMC 에서 등록된 baseline 전부: PIL / ALD / SP 한 행) + `code/run_dmc_base.sh`

- 작성: 2026-10-10 18:55 CDT (= 10-11 08:55 KST), Fable 5.1, 적대적 검토 (A 실행 가능성·코드 + B 설계·문구, 한 보고서). 코드 기준 HEAD 2b88eb53 (= 초안 커밋; `conf/code`·`Demo` dirty 0).
- 읽은 것: 초안 v1 전체; `code/run_dmc_base.sh` 전문과 그 원본 세 스크립트 `run_pilot16e4.sh`·`run_ald16e4.sh`·`run_sparse16e4.sh` 전문, `run_dmc_sparse_tune.sh`, `run_prior_eval.sh`; 커밋 ae880c27 의 diff (`dmimo.py _which`); `code/{dmimo.py, ald.py, sparse_tune.py, eval_accept.py, pair_cross.py, pair_ald.py, pair_baselines.py, run_manifest.py}` 전문; `runner.py` (`_ald_table`·`_sparse_at`·`run_task` 시행 루프·`main` 의 검사 1280–1386 행·`--prior` choices), `arms.py` 56–140 행(`load_fits`·`gmm_selection`·`build_baseline_arms`), `analysis.py` (`PAT`·`decision_points`·MIN_DISC), `score.py` (`ckpt_identity`·`best_ckpt_path`), `sigma.py load`, `common.py` (`DEV_SKIP0`·`PID`·`DM_PRIORS`·`make_gen`·`make_pilots`); 등록 `NEXT_EXPERIMENTS_{PILOT16e4,ALD16e4,SPARSE16e4}.md` §1, `STATIC16e4`·`SUPP16e4` §1–§2 의 라벨·"전부" 행, `DMC16e4.md` v2 §1(실행·수용·GMM 격자·DMC 고유 사항)·§4; `.gitignore`(루트; `conf/.gitignore` 없음) 와 `git ls-files conf/results/{sparse,ald}`; `logs/{run_pilot16e4,run_ald16e4,run_sparse16e4}.log`, `logs/tb2_post_DMC.log` 의 b\* 줄; `results/sparse/pick_UMi28_C2.json`·`results/ald/tune_PILU28.json` 의 키; `conference/figures/paper_f16deep.py` `SHOW`; `DECISIONS.md` 마지막 세 줄; `prereg_reviews_2026-10-10/review_DMC16e4.md` 머리말(형식).
- 실행한 것 (모두 CPU, `CUDA_VISIBLE_DEVICES=`, `OMP_NUM_THREADS≤4`; 수신기·BLER 실행 없음; DMC 테스트 시행 사용 없음; 저장소 쓰기는 이 파일뿐, 스크래치 `/tmp/claude-1005/-home-HTJ-t2/b187bcb3-67a6-4fa2-86ce-8a8ed017508c/scratchpad/review_dmcbase/`): ① `bash -n code/run_dmc_base.sh`; ② 스크립트의 pick 재현 heredoc 을 **UMi28** 의 기존 `pick/tune_UMi28_C2.json` 에 그대로 실행 (`pickcheck_UMi28.txt`); ③ `pair_baselines.py` 를 기존 UMi28 raw(`raw_U28B16e4`+PIL+ALD+SP, `--r0 at1 --provenance manifest`)에 `--expect` 없이 / `--expect-bstar "(i)" --expect "V1-pilot=(i)"` 로 / 틀린 `--expect-bstar "(iii)"` 로 세 번 (`dry_pairB.sh`, 출력 `pairB_U28_{noexpect,expect,wrongexpect}.txt`); ④ `gmm_fits_D2_DMCB16e4/` 15 개 fit 파일의 `ll_val` 읽기, `ckpt/d2sx_DMC_N160000_a1{,_best}.pt` 의 메타(prior·sigma_tag·role) 읽기, `nvidia-smi` 질의 + 스크립트의 awk 파싱, `ps` 로 `sparse_tune.py --prior DMC` 생존 확인 (pid 691308, 19 분 경과; 점수·로그 내용은 읽지 않음). **DMC 의 BLER·raw·tables·accept·guard·run_prior_eval 로그·sparse_tune 점수는 열지 않았다.**
- 사용자 고정 사항의 준수 (바꾸지 않음, 확인만): 11 곡선 = `paper_f16deep.SHOW` 와 초안 목록 일치(V1, ALD-pilot, b\*, R2-ours-G, R1-turbo, R3-bigamp, R0-pilot@1, SBL-loop, SBL-pilot, OMP-pilot, genie); 주 실행이 내지 않는 넷 = ALD-pilot·SBL-loop·SBL-pilot·OMP-pilot ✓; 크기(C2 8×4, n 2560 시행 0..2559, chunk 40, 7 SNR, N′ 160000, 같은 `_best`·같은 b\* 적합) 는 스크립트의 `COMMON`·링크·`eval_accept --ref-raw raw_DMCB16e4` 가 그대로 강제 ✓; "주 실행 먼저" 는 `PRIOR_EVAL_DONE`·`ACCEPT: OK` 전제 검사 ✓.

---

## 발견 (심각한 순)

### M1 · MUST · 재개(skip) 키가 **실패한 단계에서도 만들어진다** — 실패 뒤 다시 띄우면 그 단계를 건너뛰고 `pair_baselines` 까지 간다 [읽어서 확인]

- 증거 (`code/run_dmc_base.sh`): 단계 건너뛰기 키는 PIL `results/review_next/pair_PILDMC.txt` (40 행), ALD `pair_ALDDMC.txt` (55 행), SP `SPDMC_accept.txt` (78 행). 그런데 그 파일들은 `> 파일 2>&1 || die` 꼴로 쓰이므로 (48–49, 71–72, 109–110 행) **검사가 실패해도 파일은 남는다** (`pair_cross`/`pair_ald` 는 "integrity: FAILED" 를 찍고 rc 1, `eval_accept` 는 "ACCEPT: FAILED" 를 찍고 rc 1). 첫 실행은 `die` 로 멈추지만(맞음), 사람이 "일시 오류겠지" 하고 같은 명령을 다시 띄우면: PIL 의 `pair_cross` 무결성 실패 → PIL 통째 건너뜀; ALD 의 `pair_ald` 실패 → ALD 건너뜀; SP 의 `eval_accept` 실패 → SP 통째(meta|sparse 검사 포함) 건너뜀 → 마지막 `pair_baselines` 가 **무효 단계의 raw 로 라벨 15 개를 쓴다**. `pair_baselines` 자체 무결성이 일부(genie 동일, @1 동일, ALD 추정 동일, raised)는 다시 잡지만 `pair_cross` 의 "파일럿 arm 채널 추정 고정(nmse[:, t] = nmse[:, 0])", `eval_accept` 의 청크 계획·meta ntrain/bstar/kron_K/ll_val·`stagec_ckpt_id` 부재(SP) 는 잡지 않는다. 초안 §1 "실행" 의 "단계의 수용 검사가 실패하면 거기서 멈춘다(그 단계 무효)" 와 어긋나고, 원본 세 스크립트 어느 것도 이런 키를 쓰지 않는다 (`run_pilot16e4`·`run_ald16e4` 는 재개 때 전 단계를 다시 돌리고, `run_sparse16e4.sh` 32–33 행은 **출력이 있으면 ABORT**).
- 고침 (diff; 출력은 `.part` 에 쓰고 **성공했을 때만** 제 이름으로 옮긴다 → 건너뛰기 키 = 통과한 단계; 실패 출력은 `.part` 로 남아 기록이 된다. 01_RULES 의 "지우지 않는다" 와 양립):

```diff
@@ -22,2 +22,3 @@
 die () { log "ABORT: $*"; exit 1; }
+out () { local f=$1; shift; "$@" > $f.part 2>&1 && mv $f.part $f; }   # a stage output exists ONLY when that step passed (resume key)
@@ -45,8 +46,8 @@
-  $P code/eval_accept.py --prior $PR --tag $T:best:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
-    > results/review_next/${T}_accept.txt 2>&1 || die "PIL acceptance failed ($(head -1 results/review_next/${T}_accept.txt))"
+  out results/review_next/${T}_accept.txt $P code/eval_accept.py --prior $PR --tag $T:best:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG \
+    --ll-val $LL --ref-raw $BASE || die "PIL acceptance failed ($(head -1 results/review_next/${T}_accept.txt.part))"
   log "PIL acceptance ($(head -1 results/review_next/${T}_accept.txt))"
-  $P code/pair_cross.py --base $BASE --pilot raw_$T --cell $CELL --prior $PR > results/review_next/pair_$T.txt 2>&1 \
-    || die "PIL pair_cross integrity failed"
+  out results/review_next/pair_$T.txt $P code/pair_cross.py --base $BASE --pilot raw_$T --cell $CELL --prior $PR \
+    || die "PIL pair_cross integrity failed ($(head -1 results/review_next/pair_$T.txt.part | cut -c1-160))"
@@ -68,6 +69,6 @@
-  $P code/eval_accept.py --prior $PR --tag $RT:best:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
-    > results/review_next/${RT}_accept.txt 2>&1 || die "ALD acceptance failed ($(head -1 results/review_next/${RT}_accept.txt))"
+  out results/review_next/${RT}_accept.txt $P code/eval_accept.py --prior $PR --tag $RT:best:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG \
+    --ll-val $LL --ref-raw $BASE || die "ALD acceptance failed ($(head -1 results/review_next/${RT}_accept.txt.part))"
   log "ALD acceptance ($(head -1 results/review_next/${RT}_accept.txt))"
-  $P code/pair_ald.py --base $BASE --pil raw_PILDMC --ald raw_$RT --est $ET --cell $CELL --prior $PR \
-    > results/review_next/pair_$RT.txt 2>&1 || die "ALD pair_ald integrity failed"
+  out results/review_next/pair_$RT.txt $P code/pair_ald.py --base $BASE --pil raw_PILDMC --ald raw_$RT --est $ET --cell $CELL --prior $PR \
+    || die "ALD pair_ald integrity failed ($(head -1 results/review_next/pair_$RT.txt.part | cut -c1-160))"
@@ -109,2 +110,2 @@
-  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE --tag $T:-:-:$CELL \
-    > results/review_next/${T}_accept.txt 2>&1 < /dev/null || die "SP acceptance failed ($(head -1 results/review_next/${T}_accept.txt | cut -c1-80))"
+  out results/review_next/${T}_accept.txt $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
+    --tag $T:-:-:$CELL < /dev/null || die "SP acceptance failed ($(head -1 results/review_next/${T}_accept.txt.part | cut -c1-80))"
```

  초안 §1 "실행" 칸에 한 문장: `재개: 단계 출력 파일(accept·pair)은 그 단계가 통과했을 때만 생기며(실패 출력은 .part), 있으면 그 단계를 건너뛴다; pairB_SPDMC.txt 가 있으면 중단(재실행은 사용자 승인; N2)`.

### S1 · SHOULD · "전부" 문장 조건이 인용한 SPARSE16e4 §1 과 다르다 — R_{X\*} CI 하한 > 0 이 빠졌고, 문장 층위가 하나로 합쳐졌다 [실행 확인]

- 증거: SPARSE16e4 §1 "'전부' 문장 (16 개)" 행 = "원 b\* (i) **이고** 15 개 모두 (i) **이고** (ii) 0 **이고** R_{X\*} CI 하한 > 0 → '등록된 baseline 전부(16 개, 희소 baseline 포함)와 **멀어진다**'"; SUPP16e4 §2 는 두 층(k=12·m=0 → "적게 실패"; + b\* (i) + R_{X\*} 하한 > 0 → "멀어진다"). `pair_baselines.py` 295–296 행이 바로 그 조건을 `'등록된 baseline 전부와 멀어진다' condition (k = 16, (ii) = 0, R_X* CI lower > 0): MET/NOT met` 로 찍는다 — UMi28 건식 실행 출력 120 행에서 확인. 초안 §1 "'전부' 문장" 은 "b\* (i) 이고 15 개 모두 (i) → '… 전부(16 개 …)보다 적게 실패'" 만 적어 R_{X\*} 조건과 "멀어진다" 문장이 없다. 틀린 주장은 아니지만(16 개 (i) 면 "적게 실패" 는 참) "SUPP16e4 §1 그대로" 라는 선언과 어긋나고, 원고의 다른 데이터셋 문장("멀어진다")과 형식이 달라진다.
- 고침 (§1 "'전부' 문장" 칸 앞부분 교체): `DMC16e4 의 b* → V1 이 (i) **이고** 15 개가 모두 (i) ((ii) 0) → "DeepMIMO (6 개 도시 28 GHz, block split) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"; 여기에 **R_{X*}(−3 dB) 90 % CI 하한 > 0** (X* = 16 개 중 −3 dB 실패 최소, 동률 이름순; pair_baselines 의 "'등록된 baseline 전부와 멀어진다' condition … MET" 줄) 이면 SPARSE16e4 §1 과 같은 문장 "등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다" 를 쓴다 — 포화 가드·genie ≥ V1 가드로 R_{X*} 가 정의되지 않으면 '멀어진다' 문장은 쓰지 않는다(DMC16e4 §3 예측 4 "genie 가 높다" 가 맞으면 이 경우가 흔할 수 있다; 결과와 무관하게 미리 적음).`

### S2 · SHOULD · ALD β 규칙이 잘못 인용됐다 — 기준은 0.1 dB 이지 0.03 dB 가 아니다 [읽어서 확인]

- 증거: 초안 §1 "arm 과 절차" 의 "β 규칙(저자 기본값 0.005 가 0.03 dB 안이면 유지)". `code/ald.py:40` `BETA0, TIE_DB = 0.005, 0.1` 과 226 행 `res[(c0, BETA0)][0] - best <= TIE_DB`; ALD16e4 §0 (d) "개발 최적 β 가 β = 0.005 보다 개발 NMSE 를 **0.1 dB** 넘게 낫게 하지 않으면 β = 0.005". ALD16e4 26 행의 "≤ 0.03 dB" 는 6 데이터셋에서 **관측된 차**이지 규칙이 아니다. 실행은 코드가 하므로 결과는 안 바뀌지만, "절차를 그대로" 라고 선언한 문서가 규칙 상수를 틀리게 적으면 감사에서 드리프트로 읽힌다.
- 고침: `β 규칙(개발 최적 β 가 저자 기본값 0.005 보다 0.1 dB 넘게 낫지 않으면 0.005 유지; ald.py TIE_DB)`.

### S3 · SHOULD · 동결 전에 "보면 안 되는 것" 과 순서가 없다 — §2 의 예측 2 는 지금 돌고 있는 조정의 출력이고, ALD 조정값·주 실행 BLER 도 v2 전에 생길 수 있다 [읽어서 추론 + 시각 확인]

- 증거: `sparse_tune.py --prior DMC` 는 18:35 CDT 시작, 초안 비용 추정 ≈ 3.3 h (UMi28 실측 11,872 s = 3.30 h ✓) → **≈ 21:50 CDT 에 `pick_DMC_C2.json` 이 생긴다**; §2 예측 2 "OMP 의 L ≤ 4" 는 그 파일의 값이다. §1 "격자 한 판으로 끝낸다(끝값이면 끝값 + 캐비엇)" 도 pick 을 본 뒤에는 선택이 아니라 사후 결정이 된다. ALD 조정(`tune_PILDMC.json`: c·β·멈춤 단계·v)은 학습이 끝나는 대로 할 수 있고, 주 실행 BLER 은 초안 스스로 "검토·v2 동결은 주 실행과 겹칠 수 있다" 고 적었다. 그런데 §1/§2 어디에도 (a) v2 동결이 어떤 파일을 읽기 **전**이어야 하는지, (b) 동결 시각에 이미 관측된 항목을 어떻게 처리하는지(DMC16e4 가 M1 로 넣은 "관측된 항목은 예측이 아니라 관측") 가 없다. 그대로 두면 BLER 을 본 뒤 §2 1·3 의 수를 고치거나, pick 을 본 뒤 "확장 안 함" 을 고를 수 있는 창이 열려 있다.
- 고침 (§1 에 행 추가, "실행" 행 앞):
  `| **순서·열람 규칙** | v2 동결 커밋 → (학습 정지 뒤) ALD 개발 재생성·조정 → 주 실행 수용 → §5 채움·커밋 → run_dmc_base.sh. **v2 동결 커밋은 다음을 읽기 전에 한다**: results/sparse/{tune,pick}_DMC_C2.json 과 logs/sparse_tune_DMC_C2.log 의 점수·pick, results/ald/tune_PILDMC.json, 그리고 raw_DMCB16e4*·results/tables_D2_DMCB16e4*·results/review_next/{DMCB16e4_accept, recovery_DMCB16e4*}.txt·logs/{run_D2_DMCB16e4*, analysis_DMCB16e4*, run_prior_eval_DMCB16e4}.log 의 어떤 BLER·라벨·실패 수. 동결 줄(DECISIONS.md)에 그때 무엇이 존재·열람됐는지 적는다. **동결 시각에 이미 관측된 항목은 예측이 아니라 관측이다**: pick 을 읽었으면 §2 2 의 L 문장을 "관측됨 (채점 제외)" 로, 주 실행 BLER 을 읽었으면 §2 1·3 을 "관측 뒤 작성 (채점 제외)" 로 바꿔 적고, §1 의 "격자 한 판으로 끝낸다" 는 pick 을 읽기 전에 정한 것임을 동결 줄에 적는다 |`

### S4 · SHOULD · ALD 조정(수동 단계)의 명령 원문이 없다 — `ald.py estimate` 는 `--ckpt` **문자열**이 조정 기록과 같아야 통과하고, 학습이 끝나기 전의 `_best` 로 조정하면 sha 가 어긋난다 [읽어서 확인 + 파일 확인]

- 증거: `ald.py:253` `assert (smin, smax) == (rec["smin"], rec["smax"]) and a.ckpt == rec["ckpt"] and prov["ckpt_sha"] == rec["ckpt_sha"]` — 스크립트는 `--ckpt $CK`, `CK=ckpt/${ST}_best.pt` (상대 경로, 19·61 행) 를 넘기므로 `ald.py tune` 도 `~/t2/conf` 에서 **같은 상대 경로 원문**으로 불러야 한다(기존 기록 `tune_PILU28.json` 의 `ckpt` = `'ckpt/d2sx_UMi28_N160000_a1_best.pt'` 가 그 꼴; `run_scale2.sh:120` 도 `--ckpt $CKB`). 절대 경로로 조정하면 `estimate` 가 assert 로 죽고 스크립트는 "ALD estimate failed" 로 멈춘다. 또 지금 `ckpt/d2sx_DMC_N160000_a1_best.pt` 는 mtime 10-11 08:52 KST, `stopped_by None` (학습 진행 중) — 정지 전에 조정하면 `_best` 가 갱신돼 `rec["ckpt_sha"]` ≠ 파일 sha 가 되고, §5 의 `<best_sha16>` 과도 어긋난다. 초안 §4 는 "ald.py regen --set dev, ald.py tune; GPU 한 장 … 학습 종료 뒤" 만 적었다. 조정 산출물 `tune_PILDMC_curves.npz` (다른 데이터셋은 git 추적) 의 커밋 여부도 없다.
- 고침 (§1 "실행" 칸 맨 앞에): `선행(수동, ~/t2/conf 에서; 학습 정지(stopped_by 기록) 뒤): CUDA_VISIBLE_DEVICES= python code/ald.py regen --tag PILDMC --prior DMC --cell C2 --fits-tag DMCB16e4 --set dev (시행 2560..3071, CPU) → CUDA_VISIBLE_DEVICES=<빈 GPU> python code/ald.py tune --tag PILDMC --ckpt ckpt/<stem>_best.pt (**--ckpt 는 이 상대 경로 원문 그대로**: ald.py estimate 가 a.ckpt == rec["ckpt"] 와 ckpt_sha 를 assert 하고, 스크립트가 같은 문자열을 넘긴다) → results/ald/tune_PILDMC.json + tune_PILDMC_curves.npz 를 §5 와 같은 커밋에.`

### S5 · SHOULD · §2 예측 2·3 은 채점 출처·SNR 이 없어 한 가지로 채점되지 않는다; 예측 1 은 두 조건의 결합 규칙이 없다 [읽어서 추론]

- 증거: 2 "낮은 SNR 에서 작다(≤ 4)" — 어느 SNR 인지 없음; "OMP-pilot·SBL-pilot 은 R0-pilot@1 보다 적게 실패(낮은 SNR)" — `X → R0` 는 등록 쌍이 아니라 라벨이 없고, 실패 수는 `pairB_SPDMC.txt` 의 "BLER@16 failures / n per SNR" 표(UMi28 건식 출력에서 전 arm 이 찍힘을 확인)에만 있다. 3 "ALD-pilot 은 V1-pilot 보다 많이 실패" — 등록 쌍은 `pair_ald` 의 A3 (`ALDv-pilot → V1-pilot`, ALDv 이지 ALD 가 아님) 뿐. 1 "(ii) 0 개, (i) 13 개 이상" — (i) 12·(ii) 0 이면 적중인지 빗나감인지 없음.
- 고침 (§2 교체): `1. 15 개 가운데 (ii) 0 **이고** (i) ≥ 13 → 적중; 둘 중 하나라도 아니면 빗나감((iv) 는 (i) 에 세지 않는다). (i) 가 아닐 후보 …(그대로). 2. 조정 결과(채점 = pick_DMC_C2.json): OMP 의 L 이 −3·0 dB 에서 ≤ 4. BLER(채점 = pairB_SPDMC.txt 의 "BLER@16 failures / n per SNR" 표, 수치 비교·검정 없음): −3·0 dB 모두 OMP-pilot < R0-pilot@1 이고 SBL-pilot < R0-pilot@1. 3. 같은 표에서 −3·0·+3 dB 모두 ALD-pilot > V1-pilot 실패 수; 그리고 pair_ALDDMC.txt 의 A3 (ALDv-pilot → V1-pilot) = (i).`

### N1 · NIT · `nvidia-smi` 의 index 와 `CUDA_VISIBLE_DEVICES` 의 번호가 같다는 가정 (원본 `run_ald16e4.sh` 와 같음) [실행 확인]

- `CUDA_DEVICE_ORDER` 미설정(확인). 동일 GPU 6 장이라 실제로는 일치해 왔고(ALD16e4·SUPP16e4 가 이 방식으로 성공), Exclusive_Process 라 어긋나면 에러로 멈추지 조용히 틀리지 않는다. 지금 `nvidia-smi` 질의: GPU 1 만 3187 MiB(학습), 나머지 0 → awk 가 `0` 을 고른다 ✓. 원하면 33 행에 `export CUDA_DEVICE_ORDER=PCI_BUS_ID` 한 줄.

### N2 · NIT · 마지막 단계가 `pairB_SPDMC.txt` 를 덮어쓴다 — 원본 `run_sparse16e4.sh` 는 출력이 있으면 ABORT [읽어서 확인]

- 115–116 행 `echo "# run_dmc_base git …" > $O`. 같은 raw 면 결과는 결정적(부트스트랩 seed 고정)이라 수치는 같지만 머리말 HEAD 가 바뀌고 "실행은 한 번" 기록이 흐려진다. 고침: 115 행 앞에 `[ -f $O ] && die "$O exists (re-run needs user approval)"`.

### N3 · NIT · 라벨 요약 괄호가 규칙을 줄여 적었다 [읽어서 확인]

- 초안 "(i) = POWERED 이고 V1 이 ≥ 2/3 점에서 적게 실패" — `pair_baselines.table_b` 92–93 행은 **정확 양측 부호검정 p < 0.05** 인 점이 ≥ 2 여야 (i); "0.1 에 가장 가까운 3 SNR" 은 `|log10(BLER/0.1)|` 최소(`analysis.decision_points`). "SUPP16e4 §1 그대로" 가 상위 규칙이니 틀린 건 아니지만 괄호에 `(판정점마다 정확 양측 부호검정 p < 0.05)` 를 넣는 편이 안전.

### N4 · NIT · 선례 문구 "SV8e·C6 에서 pilot-only 일부가 (iv)" 는 부정확 [읽어서 확인]

- `run_sparse16e4.log`: SV8e (i) 11/15, 판정 못함 4; STATIC16e4 §0 에서 SV8e 의 (iv) 는 M-ours-bstar-scalar·M-ours-gmm32·V1-pilot (+ b\*) — 둘은 루프 arm. NR16 은 (i) 14/15 (V1-pilot (iv)). 고침: `SV8e 에서 4 개(bstar-scalar·gmm32·V1-pilot 포함), C6 에서 V1-pilot 이 (iv)`.

### N5 · NIT · `--provenance manifest` 는 DMC 의 네 raw 에 사실상 작동하지 않는다 (틀린 건 아님) [읽어서 확인]

- `pair_baselines.py:146–149`: 청크에 `run|git` 이 있으면 manifest 검사 대신 "한 개의 깨끗한 커밋" 규칙을 적용한다. DMC 의 raw 는 모두 새 runner 가 쓰므로 `run|git` 을 갖는다 → 실제 적용 규칙 = run-git. 초안 §1 "실행" 의 "raw 의 `run\|git` 은 한 커밋" 이 맞는 설명이고, "`pair_baselines --provenance manifest`" 인용은 그대로 둬도 되나 "(DMC 의 raw 는 run\|git 을 가지므로 한 커밋 규칙이 적용된다)" 를 붙이면 감사가 헷갈리지 않는다.

### N6 · NIT · 스크립트가 b\* 상수(`KK=4096`, `LL=122.37953759128766`)를 DMC16e4 §5 가 채워지기 전에 박아 넣었다 [실행 확인]

- `logs/tb2_post_DMC.log:34` `FINAL b* = kron kron_K = 4096 ll_val = 122.37953759128766`, 격자 규칙은 4096 에서 멈추므로(DMC16e4 §1) 바뀔 수 없고, 15 개 fit 파일의 `ll_val` 최대가 kron 4096 (full 최대 512: 78.547) 이라 `arms.gmm_selection` 도 같은 답을 낸다 — 값은 맞다. 다만 `eval_accept` 가 틀린 상수를 잡는 시점은 PIL 실행(≈ 10 분) **뒤**다. 원하면 36 행 앞에 한 줄: `[ "$($P -c "import numpy as np;print(repr(float(np.load('results/gmm_fits_D2_$BT/fit_${PR}_Nr8_kronK${KK}_n160000.npz')['ll_val'])))")" = "$LL" ] || die "ll_val of kron $KK != LL"`.

### N7 · NIT · "DMC 고유 1" 의 방향 주장은 맞지만 "모든 조정량" 에 대해서라는 말이 없다 [계산 확인]

- 겹침 산술 ✓: 1 − e^(−2560/52172) = 0.04788 → 512 × 0.0479 = 24.5 ("약 25") , 256 × 0.0479 = 12.3 ("약 12"); ALD 개발 = 시행 2560..3071 (`C.DEV_SKIP0 = 2560`, `--n-dev 512`; `tune_PILU28.json` n_dev 512·dev_skip 2560) ✓; SPARSE 개발 = `default_rng([20260930, 2, 11, 8, snr+100])` → `_which` 의 새 분기 → 테스트 풀 ✓. 방향: ALD 의 c·β·멈춤 단계·v(ALDv 의 plug-in 분산 = 그 단계의 개발 MSE/원소)와 SPARSE 의 ρ·n_em·L 은 **전부** 그 baseline 자신의 추정기가 테스트 분포(테스트 타일) 위에서 낸 개발 NMSE/MSE 로 고르고, V1·b\* 는 학습 타일 안에서만 고른다(DMC16e4 §1 (7)) — 어느 조정량도 테스트 분포를 보지 못한 쪽은 V1·b\* 뿐이므로 "baseline 에 유리" 는 모든 조정량에 같은 방향이다. 문구에 `(c·β·멈춤 단계·v·ρ·n_em·L 모두)` 를 넣으면 질문이 남지 않는다.

---

## 확인했고 맞는 것 (직접 검사한 것만)

- **스크립트 구문·전제 검사**: `bash -n` OK. `DECISIONS.md`·등록 파일·`results/sparse/{pick,tune}_*.json`·`results/ald/tune_*.json(+_curves.npz)` 는 이 저장소에서 **git 추적 대상**(`git ls-files` 로 UMi28 등 기존 파일 확인; 루트 `.gitignore` 는 `conf/results/gmm_fits_D2_K*/*.k0r*.npz`·최상위 `/logs/`·`*.pt` 만) → 25–27 행 검사는 §5 커밋 뒤 통과 가능. `run_prior_eval.sh` 가 `results/review_next/${TAG}_accept.txt` 와 `logs/run_prior_eval_$TAG.log` 의 `PRIOR_EVAL_DONE` 을 쓴다 ✓; `"ACCEPT: OK"` 는 정확히 10 글자라 `cut -c1-10` 비교가 맞고(두 태그 머리말 `ACCEPT: OK -- DMCB16e4, DMCB16e4last` 에도), FAILED 면 다르다 ✓. `[ ! -f $E ] || [ ! $E -nt $TJ ]` ≡ 원본의 `[ -f $E ] && [ $E -nt $TJ ] && continue` ✓. `die` 는 파이프 안이 아니라 `||` 뒤에서만 호출되고 heredoc 들의 `|| die` 도 본 셸에서 돈다 ✓. `export CUDA_VISIBLE_DEVICES=` 뒤 `CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate` 는 명령별 환경 덮어쓰기로 GPU 하나가 보인다 ✓(`run_manifest.py` 는 스스로 GPU 를 숨긴다).
- **원본 대비 단계별 인자**: PIL = `run_pilot16e4.sh` 31–40 행과 같은 `runner.py run … --pilot-arms --arm V1-pilot bstar-pilot R5-genie`, `eval_accept --tag T:best:SHA:C2 … --ref-raw raw_DMCB16e4`, `pair_cross` ✓; ALD = `run_ald16e4.sh` 26·38·48–57 행과 같은 `regen --set test --fits-tag DMCB16e4`, `estimate --tag PILDMC --ckpt $CK --set test`, `runner … --ald-file … --arm ALD-pilot ALDv-pilot R5-genie`, `pair_ald --pil raw_PILDMC --est PILDMC` ✓; SP = `run_sparse16e4.sh` 44–85 행과 같은 pick 재현 heredoc(한 글자 차이 = 주석), `runner … --sparse-file … --arm SBL-loop SBL-pilot OMP-pilot R5-genie`, `eval_accept --tag T:-:-:C2`, meta|sparse heredoc, `pair_baselines … --add-baselines … --r0 at1 --provenance manifest` 에서 `--expect-bstar`·`--expect` 만 뺌 ✓ (SP 단계에서 accept 와 meta|sparse 검사 순서만 바뀌었고 둘 다 통과해야 한다). 빠진 전제: `run_pilot16e4.sh:29` 의 fits 링크 존재 검사 → 이 스크립트는 `ln -sfn` 으로 만든다(ALD 원본과 같은 방식) ✓.
- **DMC 코드 경로** (모두 읽어서): `dmimo._which` 는 시행 스트림(7 원소) → test, 학습 스트림 7/8/10, 새 sparse_tune 스트림(5 원소, 20260930) → test; `ald.py regen` 은 `C.trial_rng` 만 쓰고(`--set dev` 는 skip 2560·n 512, `--set test` 는 0·2560) 시행당 소비 순서 `sample → integers(0,2,K) → permutation(Ns) → transmit` 가 `runner.run_task` 547–552 행과 같다 → 짝 맞음; `--rotation/--doppler` 없음이라 `sample_paths`·`.rot` 경로 미사용; `sparse_tune.py` 는 `gen.sample_vecs` + prior 무관 `SparsePrior/OMPSitePrior` 만 쓰므로 뒤 SNR 에서 prior 특정 경로로 죽을 곳이 없다(프로세스 생존 확인). `common.make_gen/make_pilots` DMC 분기 ✓, `runner --prior` choices = `C.PID`(DMC = 11) ✓, `analysis.PAT` 에 DMC ✓, `run_manifest.py` DM_PRIORS 분기(dmimo 해시·설명) ✓, `eval_accept` 의 `--prior` 는 `--grid` 때만 쓰임 ✓. 체크포인트 `d2sx_DMC_N160000_a1_best.pt` 메타 = prior DMC·sigma_tag DMC·role best(last 파일은 role last) → `ald._guard`(prior = 파일럿 파일의 prior), runner 의 ckpt-prior 검사, `eval_accept role=best` 통과 ✓; `results/sigma_grid_D2_DMC.npz` 존재 → `sigma.load("D2","DMC")` ✓. 희소 arm·`ald.py regen` 이 읽는 표본 공분산 = `gmm_fits_D2_DMCB16e4/fit_DMC_Nr8_fullK32_n160000.npz` (존재, ll_val 42.857) ✓; b\* = kron 4096 ll_val 122.37953759128766 = 15 파일 중 최대 ✓ = 스크립트 상수 ✓.
- **arm 집합·곡선**: `pair_baselines.BASELINES` 12 (R0-pilot → `--r0 at1` 로 R0-pilot@1) + `--add-baselines` 3 = 초안의 15 개와 이름까지 일치 ✓; `paper_f16deep.SHOW` 11 곡선 = 초안 목록 ✓.
- **`--expect` 없는 경로** (UMi28 건식): rc 0, 출력이 `--expect` 있는 실행과 **바이트 동일**(머리말 포함), `SUMMARY-B … (i) 15, (ii) 0`, `'전부' condition … MET` 줄 출력; 틀린 `--expect-bstar "(iii)"` 는 rc 1 "code drift" → 없으면 드리프트 검사만 빠진다 ✓ ("DMC 고유 2" 의 설명과 일치).
- **pick 재현 heredoc** (UMi28): rc 0, `rule-reproduced=True`, 메모리 필요 264 GB / 가용 1037 GB.
- **비용·선례 수치**: UMi28 조정 `wall_sec` 11871.86 ✓; 선례 (i) 15/15 = D2C2·D3·UMi28·MIX3, SV8e 11/15, NR16 14/15 (`run_sparse16e4.log`) ✓. 다중성 "새 15 + 인용 1" ✓.
- **ae880c27**: `_which` 에 분기 하나 추가, 기존 세 분기·상수 불변(diff 확인); 새 스트림은 `sparse_tune.py` 만 쓴다(`grep 20260930`).

---

## 판정

실행 가능성은 **M1 하나가 막는다**: 스크립트는 첫 실행에서는 등록대로 실패 지점에서 멈추지만, 건너뛰기 키가 실패한 단계에서도 생기므로 두 번째 실행이 무효 단계를 건너뛰어 `pair_baselines` 까지 간다 — `.part`+`mv` diff(위) 로 고치면 재개(크래시 뒤) 와 "실패 단계 무효" 가 양립한다. 그 밖의 파이썬 진입점·DMC 분기·상수·arm 집합·`--expect` 없는 경로는 읽기와 건식 실행으로 모두 통과했고, 세 원본 스크립트의 인자와 순서가 보존됐다. 설계·문구는 S1(R_{X\*} 조건과 "멀어진다" 문장을 SPARSE16e4 §1 대로), S2(β 규칙 0.1 dB), S3(동결 전 열람 금지 목록과 "관측 ≠ 예측" 규칙 — 조정 출력이 ≈ 21:50 CDT, ALD 조정·주 실행 BLER 이 v2 전에 생길 수 있어 지금 넣어야 의미가 있다), S4(ALD 조정 명령 원문·상대 경로·학습 정지 뒤), S5(예측 2·3 의 채점 출처) 를 반영하면 v2 로 동결해도 된다. 사용자가 고정한 사항(11 곡선 전부, 같은 크기·가중치·적합, 주 실행 먼저)은 모두 지켜졌고, "DMC 고유" 두 공개는 산술·방향 모두 정확하다.
