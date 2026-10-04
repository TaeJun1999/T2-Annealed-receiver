# NSCALE 등록 검토 원문 — 라운드 5 (워크플로 wf_1d727603-a0f; 작성자 Opus 5.5, 검토자 Fable 5.1 두 관점)

## 작성자 보고

라운드 5 반영을 마쳤습니다. 반드시 2 건과 권고 (a)–(f) 를 두 파일에 넣었고, (g) 는 지시대로 넣지 않았습니다. 수정 뒤 `bash -n` 과 모든 harness 가 통과했습니다. 커밋, GPU, BLER, 삭제 명령은 쓰지 않았고, 시각은 `{{NOW}}` 로 남겼습니다.

**`run_nscale.sh`**
- **`done()`**: integ4-M1 문안 그대로 바꿨습니다. 이제 `# =====` 머리말과 `# done`·`# resume` 줄을 로그 순서로 내놓습니다. 머리말 주석의 `prep` 설명 한 줄도 맞췄습니다.
- **(d) `gl`**: GB′ 로그 줄 앞에 로그 파일 이름을 붙입니다 (`sorted(glob)`).
- **(f) K8 줄 검사**: `[[ $K8RUN =~ ^[01]$ ]] || die "$S5: K8 line missing (K8 <kron_K> <ll_val> <1|0>)"` 을 넣었습니다. 전에는 K8 줄이 없으면 빈 값이 조용히 0 이 됐습니다.

**`NEXT_EXPERIMENTS_NSCALE.md` (v4)**
- **머리말**
  - 제목과 상태를 v4 로 올렸습니다.
  - 검토 표에 4차 행을 넣었습니다.
  - "4차 적대적 검토 반영" bullet 을 더했습니다. 내용은 반영, 주 세션 결정, 열람, 확인입니다. 3차 bullet 은 이력으로 그대로 두고, 4차 bullet 에 "첫 `# done` → 구간 규칙" 정정을 적었습니다 (권고 c).
  - DECISIONS 동결 줄 항목에 "4차 주 세션 결정 1 건" 을 더했습니다.
- **M1 구간 규칙**: 주 세션 결정대로 한 규칙을 다음 자리에 모두 썼습니다.
  - §5 체크포인트 행
  - §5 D1 형제 행 (`logs/train_sx_N<N>_D1[_fb<k>].log`)
  - §1 수용 (c)
  - §1 보고 전용 행
  - §1 학습 실패 행 (§3d 판정 줄)
  - §1 자격 행 (csv 대조 줄)
  - §1 실행 스크립트 행
  - 예측 5 (채점 줄)
- **M2**: S_N 개수 문장을 검토 문안 그대로 넣었습니다. 쓰기 전에 기준점 표 B 줄을 직접 확인했습니다. 여섯 파일 `tables_D2_{B1e4,B4e4k,B16e4k,B32e4,NR16run2,NR16B16e4}.txt` 모두 블록이 1 개씩이고, `POWERED` 이며 `second arm fewer 3/3` 입니다. pooled 값 (502:72 / 459:79 / 454:78 / 421:69 / 266:13 / 213:18) 은 §0 과 같습니다.
- **(a)**: §3 머리말에 '동결 전 확인' bullet 을 넣었습니다. 대상 예측은 2·3·4·5·6·16 입니다. 검토 목록에 있던 17 은 CPU BLER 로만 답할 수 있어서 뺐습니다.
- **(b)**: S_N C2 문장의 "V1 쪽 (i)" 을 "'통과' (C6 의 (i) 에 해당)" 로 고쳤습니다.
- **(e)**: §4.1 GB′ 행에 `gbp_watch.sh` 를 직접 읽고 그 동작을 적었습니다.
  - 120 s 마다 태그별로, 최종 병합 적합 15 개 (full 6 + kron 9, 후보 파일 제외) 가 있고 학습 작업이 `gpu_sched.log` 에 `done rc=0` 이면 큐에 넣습니다.
  - 큐에 넣는 줄은 §4.1 의 세 명령과 같고, 우선순위 90, flock, 태그마다 한 번입니다.
  - 학습 로그에 `diverged` 가 있거나 rc ≠ 0 이면 넣지 않고 ALERT 만 남깁니다.
- §1 실행 스크립트 행의 전제 목록에 "`K8` 줄 존재" 를 더했습니다.

**확인** (스크래치 `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/nscale_reg/r6/`)
- **`done()` + 구간 규칙** (`t_done_r6.txt`, assert 통과):
  - (A) 정상 학습 + GB′ 쌍: 학습 구간 1, 최종 줄 patience, 학습 9000.0 s.
  - (B) 중단 → 재개 → GB′ 쌍: 최종 줄은 중단 줄이 아니라 재개 구간의 patience 줄, 학습 100 + 8900 = 9000.0 s.
  - (C) 죽은 구간 + 재개 + GB′ 쌍: 죽은 구간 1, 학습 8600.0 s 를 하한으로 표기.
  - 기준 로그 3 개: 학습 40953.8 / 36743.4 / 7929.9 s, 죽은 구간 0.
- **`prep` (기준 두 점)**: 라운드 4 블록을 먼저 같은 거울에서 돌려 라운드 4 출력을 바이트 그대로 재현했습니다. 새 블록 출력은 `training:` 세 줄만 다르고, 각 줄에서 `# =====` 항목을 빼면 라운드 4 와 같습니다 (assert). 가짜 GB′ 로그 2 개로 `gl` 이 두 파일을 이름으로 구별하는 것도 확인했습니다.
- **전제**: 라운드 4 의 7 경우는 출력이 바이트 동일합니다. 새로 넣은 두 경우, K8 줄 없음과 run 필드 없음은 모두 ABORT 합니다.
- **나머지**: `qk`·`why` (6·6 경우) 는 바이트 동일, 단일 S5 8 경우는 PASS 4·ABORT 4 가 같은 자리에 나옵니다. 조각은 현재 스크립트에서 다시 뽑았고, 바뀐 조각은 K8 줄 하나입니다.

**주 세션이 정할 것 3 건** (고치지 않았습니다)
1. **M2 문안의 사유 괄호**: "게이트 FAIL 은 '예산 축 측정' 표기" 가 '통과 아님' 사유 목록 안에 들어 있습니다. 그런데 S_N C2 는 D1 게이트와 무관하게 표 B 로만 판정하므로, 게이트 FAIL 이면 통과가 아니라고 잘못 읽힐 수 있습니다. 지시대로 문안은 그대로 넣었습니다.
2. **감시 스크립트와 중단된 학습**: `--no-gbprime` 학습이 SIGINT 로 중단되어 `aborted=True` 가 되어도 rc=0 으로 끝납니다 (`run_d2_sx.py:77–80` 의 `sys.exit(0)`). 그래서 적합 15 개가 갖춰져 있으면 `gbp_watch.sh` 가 GB′ 를 큐에 넣고, 그 GB′ 작업은 `# resume` 줄 없이 학습을 이어서 돌립니다. 구간 규칙은 이 구간을 학습으로 맞게 셉니다. 다만 GB′ 작업이 긴 학습 작업이 됩니다.
3. **머리말만 있는 로그**: 새 `done()` 은 머리말만 있는 로그에 대해 `(no '# done' line …)` 대신 머리말 줄을 내놓습니다. integ4-M1 문안 그대로이고, 구간 규칙에서는 죽은 구간으로 셉니다.

파일:
- /home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md
- /home/HTJ/t2/conf/code/run_nscale.sh

## 검토 — 관점 stats-fair

### must
- **stats-fair r5 M1** (NEXT_EXPERIMENTS_NSCALE.md §2.2 합성 문장 S_N 끝 문장 (:188 마지막 문장 "'통과 아님' 인 새 점은 사유 (게이트 FAIL 은 '예산 축 측정' 표기, …) 를 괄호로 덧붙인다"))
  - 문제: r4 M2 문안 (검토자 문안 그대로) 의 사유 괄호가 '게이트 FAIL' 을 '통과 아님' 의 사유 목록 첫 항목으로 넣어 두 읽기가 생긴다. 같은 항목의 앞 문장은 "D1 게이트와 무관하게 표 B 출력으로만 판정", k = "표 B `b* → V1` 이 '통과' 인 점 수" 라 게이트 FAIL + 표 B 통과인 새 점은 k 에 들고 S_N 문장이 성립한다 (표기만 '예산 축 측정'). 그런데 끝 괄호는 게이트 FAIL 을 '통과 아님' 사유로 읽히게 한다 → 같은 점이 k 에서 빠지고 개수 문장으로 떨어진다. 구체 경로: `B64e4` 의 D1 게이트가 FAIL (§3 18 (c) 가 빗나감 경로로 명시; 게이트는 §5 에 BLER 전 고정) 이고 표 B 가 통과이면 `FALLBACK 0` 에서 k = 6 (S_N 성립, 'D2 C2 … 모든 예산 점에서 통과') 또는 k = 5 ('6 개 중 5 개') 를 전사자가 표 B 를 본 뒤 고른다 — 문장 형태 자체가 결과 뒤 선택이 된다. 드래프터 보고의 '주 세션이 정할 것 1' 과 같다.
  - 수정: :188 의 "'통과 아님' 인 새 점은 사유 (게이트 FAIL 은 '예산 축 측정' 표기, `PT <tag> -`, 수용 실패, 통과 못함 (출력 문자열)) 를 괄호로 덧붙인다." 를 다음으로 교체: "'통과 아님' 인 새 점은 사유 (`PT <tag> -` (학습·적합 실패), 수용 실패 (표 B 없음), 통과 못함 (출력 문자열)) 를 괄호로 덧붙인다. **D1 게이트 FAIL 은 '통과 아님' 의 사유가 아니다**: k 와 S_N 성립 여부는 위 조건대로 표 B 출력으로만 정하고, 게이트 FAIL 인 새 점은 표 B 가 '통과' 면 k 에 들되 '예산 축 측정' 표기를 옆에 붙인다 (§2.1 FAIL 행; arm 주장에는 쓰지 않는다)." 머리말 4차 bullet 의 r4 M2 항목 끝에 "(5차: 사유 괄호에서 게이트 FAIL 을 뺌 — 게이트는 표기만, k 와 무관)" 을 덧붙인다.
- **stats-fair r5 M2** (NEXT_EXPERIMENTS_NSCALE.md §1 '학습 실패' 행 (:125 "`aborted = True` (중단) 는 §3d 가 아니라 같은 시행을 재개한다") · §4.1 GB′ 재실행 행 (:252, 권고 (e) 로 들어온 `gbp_watch.sh` 동작 서술))
  - 문제: 두 문장이 같은 체크포인트에 두 재개 작업을 만든다. (1) `score.train` 은 Ctrl-C/SIGINT 를 잡아 `# done … stopped_by=interrupted, aborted=True` 를 쓰고 정상 반환한다 (score.py :1030–1031); `run_d2_sx.py --no-gbprime` 은 `sys.exit(0)` (:77–80), `train_nr16.py --no-gbprime` 은 `return 0` (:68–69) → 중단된 학습도 **rc=0** 이다. (2) `gbp_watch.sh` 는 `aborted` 를 보지 않고 '병합 적합 15 개 + `done rc=0`' 만으로 GB′ 작업을 큐에 넣는다 (:14–16); 그 GB′ 작업은 `_already_stopped` 가 None (score.py :737–746: 중단 상태는 patience/max/diverged 어느 것도 아님) 이라 `# resume` 없이 같은 ckpt 로 학습을 이어 돈다. (3) 동시에 §1 은 주 세션이 '같은 시행을 재개' 하라고 한다 → `--no-gbprime` 재개가 따로 큐에 들어가면 두 작업이 서로 다른 GPU 에서 (Exclusive_Process 는 GPU 단위) 같은 `ckpt/<stem>.pt`·`<stem>_best.pt`·`logs/train_<stem>.log` 를 동시에 쓴다. 결과: ckpt 는 마지막 저장자가 이기고 (eval 의 sha 검사는 S5 와의 일치만 보므로 출처를 가리지 못함), 로그는 두 `# =====` 머리말 뒤에 두 `# done` 이 끼어 들어 4차에서 채택한 구간 규칙이 틀린 줄을 고른다 → §5 기록·학습 초·예측 5 채점이 복구 불가능하게 오기록된다. 경로는 구체적이다: V1 학습 (우선순위 90, 중앙 11 h, 1.28e6 최대 138 h) 이 격자 (85/50) 보다 오래 돌아 15 개 적합이 먼저 갖춰지는 것이 보통이고, 중단은 주 세션이 GPU 를 비우려 작업을 죽일 때 (메모리 노트 'map pid→session before killing') 생긴다. 반대로 SIGKILL·OOM (rc ≠ 0) 이면 감시가 그 태그를 `left` 에서 버려 (:17) GB′ 가 자동으로는 영원히 들어가지 않는데 문서는 §3d 경우만 '주 세션이 직접 넣는다' 고 적었다. 드래프터 보고의 '주 세션이 정할 것 2' 와 같다.
  - 수정: (1) :125 의 "`aborted = True` (중단) 는 §3d 가 아니라 같은 시행을 재개한다." 뒤에 삽입: "**재개는 작업 하나만**: `gbp_watch.sh` 는 rc 만 보고 `aborted` 를 보지 않으며 중단된 `--no-gbprime` 학습도 rc=0 이므로 (score.py :1030–1031, run_d2_sx.py :77–80, train_nr16.py :68–69), 그 태그의 격자 적합 15 개가 이미 있으면 감시가 GB′ 작업을 큐에 넣고 그 작업이 `# resume` 없이 같은 ckpt 의 학습을 이어 마친다 (`_already_stopped` 가 None). 그 GB′ 줄이 `gpuq.txt` 에 있거나 돌고 있으면 `--no-gbprime` 재개를 따로 넣지 않는다; 없으면 (적합 15 개 미완, 또는 rc ≠ 0 로 감시가 태그를 버림) `--no-gbprime` 재개를 넣고 끝난 뒤 GB′ 를 주 세션이 직접 넣는다. 같은 ckpt 를 두 작업이 동시에 쓰면 체크포인트·로그 구간이 섞여 §5 체크포인트 행의 구간 규칙이 복구되지 않는다 — 넣기 전에 `gpuq.txt` 와 `gpu_sched.log` 에서 그 stem 의 작업이 없음을 확인하고 §5 에 적는다." (2) :252 의 "학습 로그에 `stopped_by=diverged` 가 있거나 학습 작업 rc ≠ 0 이면 넣지 않고 ALERT 만 남긴다" 뒤에 삽입: "(감시는 `aborted=True` 를 보지 않는다: 중단된 학습 (rc=0) 도 적합 15 개가 있으면 GB′ 로 큐에 넣고 그 GB′ 작업이 학습을 이어 마친다 — §1 학습 실패 행 '재개는 작업 하나만'; rc ≠ 0 로 버려진 태그는 재개와 GB′ 를 모두 주 세션이 직접 넣는다)". (3) 머리말 4차 bullet 의 권고 (e) 항목 끝에 "(5차: 중단 학습과의 이중 재개 금지 규칙을 §1 학습 실패 행에)" 를 덧붙인다. `gbp_watch.sh` 자체의 가드는 대상 밖 (권고 참조).

### should
- §3 머리말 '동결 전 확인' (:221) "적중으로 세지 않는다" → "적중·빗나감 어느 쪽으로도 세지 않고 (채점 제외) '동결 전 확인 (<관측값>)' 으로만 기록한다" — 지금 문장은 빗나감으로 셀지 열려 있어 '적중은 불가·빗나감은 가능' 읽기가 남는다 (예측 1 의 처리와 같게 한 범주로).
- `prep` (run_nscale.sh :126 뒤): §3d 가 적용되면 S5 의 stem 은 `_fb<k>` 인데 `prep` 은 `NEW` 의 a1 stem 만 ident·`done()` 을 찍는다 (D1 은 :142–143 에서 `_fb*` 전부를 찍는다) → §5 체크포인트 행의 "`prep` 출력 그대로" 를 fb stem 에서 지킬 수 없다. D1 과 같은 꼴로 한 블록 추가: `for p in sorted(glob.glob(f"ckpt/{stem}_fb*.pt")):` / `    if p.endswith("_best.pt"): continue` / `    fs = os.path.basename(p)[:-3]` / `    for x in (ident(f"ckpt/{fs}_best.pt"), ident(p)): print("  ckpt " + (x if isinstance(x, str) else x[0]))` / `    print(f"  training {fs}: {done(fs)}")` (예측 5 의 채점 줄은 a1 로그라 지금도 찍힌다; 바뀌는 것은 fb stem 의 §5 전사 근거).
- §2.2 S_N C2 문장 틀 (:188) 괄호 "1e4·4e4 는 D1 형제 게이트 FAIL = 예산 축 측정, 1.6e5 이상은 PASS 레시피" → "1e4·4e4 는 D1 형제 게이트 FAIL = 예산 축 측정, 1.6e5·3.2e5 는 PASS 레시피, 새 점은 §5 의 게이트 그대로 (FAIL = 예산 축 측정)" — 새 점이 FAIL 이면 '1.6e5 이상은 PASS' 가 거짓이 되어 전사자가 문장을 손봐야 한다 (라벨은 바뀌지 않음).
- 주 세션 스크립트 `logs/nscale/gbp_watch.sh` (대상 밖, 선택): :16 의 큐 조건에 `! tail -n 3 $M/logs/${TL[$t]} | grep -q 'aborted=True'` 를 더하면 중단 학습을 GB′ 로 넣지 않고 ALERT 로 남길 수 있다 — M2 의 문서 규칙만으로도 이중 재개는 막히므로 선택.

### verified
- 4차 반드시 2 건이 모든 자리에 있음: 구간 규칙 — run_nscale.sh :94–98 `done()` (integ4-M1 문안과 바이트 동일; 스크래치 `r6/dn/fn.py` 와 diff 없음), 문서 §5 체크포인트 행 :280, §5 D1 형제 행 :282 (`logs/train_sx_N<N>_D1[_fb<k>].log`), §1 수용 (c) :137, §1 보고 전용 :136, §1 학습 실패 :125 (§3d 판정 줄), §1 자격 :126 (csv 대조 줄), §1 실행 스크립트 :139, 예측 5 :227 (채점 줄) — 아홉 곳 모두 '학습 구간 중 마지막 `# done`, wall 합, 죽은 구간 수·하한' 한 규칙. r4 M2 — :188 끝 문장이 검토 문안 그대로 (C2 n 6/5·k 표 B 통과, C6 n 3·k (i), 기준점 몫 C2 4 점·C6 2 점 POWERED·3/3 고정, k 범위 {4,5,6}/{4,5}·{2,3}).
- 구간 규칙을 내가 따로 구현해 기준 로그 3 개 (`# =====`·`# done`·`# resume` 줄만 필터) 에 적용: `train_d2sx_N320000_a1` 구간 2 (학습 1·GB′ 1), wall 합 40953.8 s, 최종 줄 patience·aborted=False·986 epochs; `train_d2sx_NR16_N160000_a1_fb2` 구간 1, 36743.4 s, 1704 epochs; `train_sx_N320000_D1` 구간 1, 7929.9 s, 200 epochs; 죽은 구간 0 — 드래프터 `r6/t_done_r6.txt` 의 값과 일치. 가짜 로그 A/B/C (정상+GB′ / 중단 100 s → 재개 8900 s → GB′ / 머리말만 죽은 구간 + 8600 s + GB′) 의 assert 통과를 파일로 확인: B 의 최종 줄 = 재개 구간 patience 줄 (중단 줄 아님), 합 9000.0; C 는 killed 1·lower_bound True.
- 스크래치 조각이 현재 스크립트와 바이트 동일: `pre_pt.sh` = :232–256 (25 줄, K8 줄 검사 :254 포함), `pre_fb.sh` = :224–225, `guard_pre.sh` = :216–219, `guard_write.sh` = :261, `qk_fn.sh` = :449–463, `why_fn.sh` = :412–416, `dn/fn.py` = :94–98. `r6/t_pre.out` 9 경우: A 정상 (FB 1 + `PT B128e4 -` + C6 `- - -`@4096 + K8 1) PASS, B `PT B128e4 C2 1280000 -` ABORT, C gate '?' ABORT, D K2 집합 `kronK4096_` ABORT, E K8 1 + 8192 없음 ABORT, F K8 1 + `PT B64e4 -` ABORT, G `PT B64e4 -` + K8 0 PASS, **H K8 줄 없음 ABORT (`K8 line missing`), I `K8 8192 -3.2` ABORT** — 권고 (f) 가 전과 달리 조용한 run 0 을 막는다. `t_single.out` 8 경우 PASS 4·ABORT 4 같은 자리; `t_qk_why.out` 6+6 경우가 §1 Q-K (가) 세 강제 조건·r ≥ 1·§1 가드 사유 분류와 일치.
- `prep` 기준 두 점: `r6/t_prep_r4code_in_r6.txt` 대 `t_prep_r5_single.txt` 의 diff 는 `training:` 세 줄 (B32e4 :28, D1 :30, NR16B16e4 :60) 뿐이고 각 줄은 `# =====` 항목이 더해진 것 외 동일 (b*·r·c_K·K2·sha·DRAFT 줄 불변). `gl` (:148–149): 가짜 GB′ 로그 2 개가 `gbp_FAKEC2.log: …`·`gbp_NR16FAKEC6.log: …` 로 파일별 구별 (`t_prep_r5_gl.txt` :32); glob 은 `sorted`.
- §4.1 GB′ 행의 감시 스크립트 서술이 `logs/nscale/gbp_watch.sh` 와 일치 (이 검토에서 읽음; 결과 아님): 15 개 조건 glob `fit_S2_Nr<nr>_*_n<N>.npz` 는 `.k0r*.npz` 후보를 제외 (접미 불일치), `done rc=0 job_g.: .*<--no-gbprime 명령>` grep, `stopped_by=diverged` → ALERT·태그 제거, rc ≠ 0 → ALERT·태그 제거, 우선순위 90·flock·태그마다 한 번·120 s 주기·로그 `gbp_<T>.log`. 다만 `aborted` 미검사 → M2.
- M2 의 코드 근거: score.py :1030–1031 `except KeyboardInterrupt: stopped, aborted = "interrupted", True` 뒤 정상 반환·`# done` 기록 (:1035–1036); run_d2_sx.py :77–80 `if a.no_gbprime: sys.exit(0)`; train_nr16.py :68–69 `if a.no_gbprime: return 0` (`sys.exit(main())` :93); `_already_stopped` (score.py :737–746) 는 diverged/patience/max_epochs 만 돌려 중단 상태에서는 None → 재개 작업이 학습을 이어 돈다. 두 재개 작업이 같은 `ckpt/<stem>.pt`·`logs/train_<stem>.log` 를 쓰는 경로는 §1 :125 + §4.1 :252 두 문장에서 바로 나온다.
- `bash -n code/run_nscale.sh` 통과 (이 검토). 두 대상 파일과 `results/review_next/prereg_reviews_nscale/` 는 `??` (미추적, 커밋 없음). 머리말 4차 행·bullet·DECISIONS 줄 (:10, :33–38, :143) 의 반영 수 (반드시 3 → 병합 2 + 주 세션 결정 1, 권고 8 중 6 반영·1 흡수·1 생략) 가 round-4 검토 두 건의 must·should 수와 맞는다. 예측 5 의 'F1 미발동' 채점 유지 (:220 끝 문장) 와 F1 때 1.28e6 몫 미채점은 주 세션 결정대로.
- 읽지 않은 것: NSCALE 학습 로그 (`logs/train_d2sx_N640000_a1.log`·`N1280000`·`NR16_N640000`·`train_sx_N*_D1` for N ≥ 6.4e5), NSCALE 적합 npz·적합 로그, `samplecx.csv` 새 행, `~/t2_wtS` 의 어떤 파일 (gpu_sched.log·gpuq.txt·SEEDSNR·`*NR32_N160000_a3_fb3*` 포함), 새 예산의 BLER. 열람: 기준 로그 3 개의 `# =====`·`# done`·`# resume` 줄만 (필터 출력), `code/score.py` :737–746·:915–960·:1020–1040, `run_d2_sx.py` :50–85, `train_nr16.py` :55–70, `run_samplecx.py` 머리말, `logs/nscale/gbp_watch.sh`, 스크래치 `nscale_reg/r6/`. GPU·BLER·커밋·삭제 없음; 스크래치 `nscale_reg/fable_r6/done_now.py` 한 파일만 남겼다.

## 검토 — 관점 integ

### must
- **integ5-M1** (run_nscale.sh :237–252 (eval 전제 NEW 루프; :243 뒤) · NEXT_EXPERIMENTS_NSCALE.md §1 실행 스크립트 행 (전제 목록) · §1 체크포인트·평가 가중치 행 "(§3d 시행이면 `_fb2`/`_fb3` stem; §5 가 정한다)")
  - 문제: S5 의 stem 이 발산·중단·미완 학습의 것이어도 eval 전제가 전부 통과한다. `prep` 의 DRAFT PT 줄은 항상 attempt 1 stem 과 그 ckpt sha 를 쓰고 (:121–122, :154; `_fb*` 는 :126 에서 파일명만 나열), 발산한 attempt 1 의 `ckpt/<stem>{,_best}.pt` 는 디스크에 그대로 남는다 (선례: `logs/train_d2sx_NR16_N160000_a1.log:1076` `stopped_by=diverged, aborted=False`, `ckpt/d2sx_NR16_N160000_a1{,_best}.pt` 가 fb2·fb3 옆에 존재). eval 전제는 stem 을 `^$STEM(_fb[23])?$` 로만 (:241), ckpt 는 sha 일치로만 (:242–243) 검사하고 학습 로그는 어디서도 읽지 않는다 → DRAFT 줄을 그대로 S5 에 옮기면 (예측 18 (b) 의 §3d 경로에서 실제로 생기는 실수) 발산 체크포인트가 등록 태그로 평가된다 — §1 학습 실패 행 "발산 체크포인트로 평가하지 않는다" 를 스크립트가 지키지 못함. 중단 (`aborted=True`) 뒤 재개하지 않은 학습, 머리말만 남은 죽은 구간도 같다 (부분 ckpt 의 sha 는 일치). S5 는 단일이라 잘못 돌면 사용자 승인 + DECISIONS 비용. '있는 가장 뒤 시행 = 정답' 규칙은 쓸 수 없다 (C6 기준의 fb3 로그 `train_d2sx_NR16_N160000_a1_fb3.log` 는 :2 머리말만 있고 `# done` 이 없는데 fb2 가 기록 가중치) — §5 체크포인트 행의 구간 규칙 줄 자체를 읽어야 한다. 확인 (`nscale_reg/r7/`): 아래 두 줄이 기준 로그 3 개 (B32e4 a1 — GB′ 재개 쌍 포함 —, NR16B16e4 fb2, D1 3.2e5) 에서 PASS, 가짜 로그 A(정상+GB′)·B(중단→재개→GB′)·C(죽은 구간+재개+GB′) PASS, 머리말만 / interrupted 만 / diverged / diverged + 뒤의 no-epoch 재실행 / 로그 없음 → 모두 ABORT.
  - 수정: run_nscale.sh :243 (`last-EMA … sha256 differs`) 바로 뒤에 두 줄 삽입:
```
  TL=$(awk '/^# =====/{s++; r[s]=0} /^# resume/{r[s]=1} /^# done/{if (!r[s]) l=$0} END {print l}' logs/train_$3.log 2>/dev/null)   # last '# done' of a training segment (§5 체크포인트 행 구간 규칙; '# resume' segments = GB' re-runs)
  [[ $TL == *"aborted=False"* && $TL != *"stopped_by=diverged"* ]] || die "$T: logs/train_$3.log final training '# done' = '${TL:-missing}' (a diverged / interrupted / unfinished attempt is never evaluated; §1 학습 실패)"
```
문서 §1 실행 스크립트 행 전제 목록의 "점마다 14 필드·sha·격자 = 등록 격자·gate (C2: PASS\|FAIL, C6: UNGATED)·K2 조건·링크" 를 "점마다 14 필드·sha·격자 = 등록 격자·gate (C2: PASS\|FAIL, C6: UNGATED)·K2 조건·링크·**S5 stem 의 학습 로그** `logs/train_<stem>.log` 의 마지막 학습 구간 `# done` (구간 규칙; `# resume` 구간 제외) 이 `aborted=False` 이고 `stopped_by=diverged` 가 아님 (줄이 없으면 ABORT)" 로. §1 체크포인트·평가 가중치 행의 "(§3d 시행이면 `_fb2`/`_fb3` stem; §5 가 정한다)" 를 "(§3d 시행이면 `_fb2`/`_fb3` stem; §5 가 정한다 — `prep` 의 DRAFT 는 attempt 1 stem·sha 를 쓰므로 손으로 바꾼다; eval 전제가 S5 stem 의 학습 로그 최종 학습 `# done` 이 발산·중단·미완이면 ABORT 한다)" 로. 머리말 4차 bullet 끝 (또는 5차 bullet) 에 "integ5-M1 → eval 전제에 S5 stem 학습 로그 검사" 한 줄.

### should
- `prep` :121–127 을 attempt 1 + `_fb[23]` stem 전부에 대해 돌려 ident·`training:` 줄을 찍을 것 (지금은 :126 에서 `_fb*` 파일명만) — §3d 점의 §5 체크포인트 행을 prep 출력으로 전사할 수 있게: `for s_ in [stem] + [os.path.basename(p)[:-3] for p in sorted(glob.glob(f"ckpt/{stem}_fb[23].pt"))]:` 아래로 :122–125·:127 을 들여쓰고 `print(f"  training {s_}: {done(s_)}")`; DRAFT 는 attempt 1 그대로 두고 `§3d: attempts present …` 한 줄만 더한다 (M1 의 전제가 잘못 옮긴 stem 을 거부한다).
- §2.2 S_N 끝 괄호 (드래프터 미결 1): "'통과 아님' 인 새 점은 사유 (게이트 FAIL 은 '예산 축 측정' 표기, `PT <tag> -`, 수용 실패, 통과 못함 (출력 문자열)) 를 괄호로 덧붙인다." → "'통과 아님' 인 새 점은 사유 (`PT <tag> -`, 수용 실패, 통과 못함 (출력 문자열)) 를 괄호로 덧붙이고, 게이트 상태 (FAIL 이면 '예산 축 측정') 는 통과 여부와 별개로 모든 새 점 옆에 적는다." — k 정의 (표 B 만) 자체는 이미 명확해 반드시는 아님.
- §4.1 GB′ 행 (드래프터 미결 2, 주 세션 몫): `--no-gbprime` 학습이 SIGINT 로 끝나면 `aborted=True` 인데 rc 0 (`run_d2_sx.py` :79–80 `sys.exit(0)`) 이라 `gbp_watch.sh` 는 '학습 끝' 으로 보고 적합 15 개가 있으면 GB′ 를 큐에 넣고, 그 GB′ 작업이 학습을 이어 끝낸 뒤 GB′ 를 계산한다 (구간 규칙은 그 구간을 학습으로 맞게 센다; M1 전제도 통과). 다만 주 세션이 같은 ckpt 의 재개를 따로 큐에 넣으면 두 작업이 같은 ckpt·로그를 동시에 쓴다 — "학습은 완료 상태로 건너뜀" 옆에 "(중단 (`aborted=True`) 학습은 rc 0 이라 감시 스크립트가 GB′ 를 넣고 그 작업이 학습을 이어 끝낸다; 재개를 따로 넣지 않는다)" 한 줄.
- `done()` :98 의 대체 문구 `(no '# done' line in …)` 은 이제 로그 자체가 없거나 머리말도 없을 때만 나오므로 `(no '# =====' / '# done' line in {lg})` 로 (머리말만 있는 로그는 머리말을 내놓고 구간 규칙이 죽은 구간으로 센다 — 드래프터 미결 3, 동작은 맞음).

### verified
- `bash -n code/run_nscale.sh` 통과 (이 검토). 드래프터 r6 조각이 현재 스크립트와 바이트 동일: `dn/fn.py` done() = :94–98, `qk_fn.sh` = :449–463, `why_fn.sh` = :412–416, `guard_write.sh` = :261, `guard_pre.sh` = :216–219, `pre_fb.sh` = :224–225, `pre_pt.sh` = :232–256 (diff).
- integ4-M1 `done()` (:94–98) = 검토 문안 그대로 (`# =====`·`# done`·`# resume` 를 로그 순서로 ` || ` 연결). score.py 가 `# =====` 를 쓰는 곳은 :919 (실행마다 1 회) 뿐, `# resume` 은 :957 (`_already_stopped` 참일 때만, 문구 'no epoch trained'), `# done` 은 :1036 (`aborted={aborted}` → `aborted=False|True`, `stopped_by=interrupted` :1032) — 구간 규칙의 전제 (머리말 1 = 실행 1, GB′ 재실행 = `# resume` 구간) 가 코드와 맞다. 독립 하네스 (`nscale_reg/r7/fn.py`, 스크립트에서 그대로 추출): A → 학습 1·GB′ 1·죽은 0, 최종 patience; B → 학습 2 (중단 줄 아님), wall 합; C → 학습 2·죽은 1·하한; 머리말만 → 학습 1·죽은 1·최종 없음. 기준 로그 3 개: B32e4 :2·:994 (40953.8 s)·:996·:1002–1003 (GB′ 쌍 3.3 s), NR16B16e4 fb2 :2·:1712 (36743.4 s), D1 :2·:208 (7929.9 s) — 문서 4차 '확인' bullet 과 같다.
- 권고 (d) `gl` (:148–150): `sorted(glob)` + `basename: 줄`; GB′ 출력 문자열 `[d2sx] GMM b* = … @N={gmm_n}` (run_d2_sx.py :88) · `[nr16] GMM b* = … @N={a.ntrain}` (train_nr16.py :83) 이 필터 `"GMM b* ="`·`@N={n}` 과 맞고, GB′ npz 이름 `results/d2_gbprime_{tag}.npz` (run_d2_sx :98 → `d2_gbprime_N640000_a1.npz`, train_nr16 :85 → `d2_gbprime_NR16_N640000_a1.npz`) 이 prep :151 의 glob 과 맞다.
- 권고 (f) K8 전제 (:253–254): `[[ $K8RUN =~ ^[01]$ ]]` — 줄 없음 (빈 값)·`K8 8192 -3.2` (run 필드 없음)·5 필드 (`read` 가 나머지를 셋째 변수에 몰아 `0 x`) 모두 ABORT, `K8 - - 0` PASS; 드래프터 `t_pre.out` H·I 가 ABORT. `links` :207–208 은 검사 없이 run 1 일 때만 B64e4k8 집합을 만든다 (eval 이 뒤에서 거부하므로 안전).
- 권고 (e) §4.1 GB′ 행 ↔ `logs/nscale/gbp_watch.sh` (주 세션 스크립트, 결과 아님): sleep 120, 태그별 CMD = §4.1 세 명령 (`run_d2_sx.py --ntrain 640000 --tag B64e4` / `--ntrain 1280000 --tag B128e4` / `train_nr16.py --nr 16 --ntrain 640000 --fits-tag NR16B64e4`), 로그 `$M/logs/nscale/gbp_$t.log`, 우선순위 90·`flock $S/gpuq.txt.lock`·태그마다 한 번 (`left` 에서 제거), 조건 (1) `fit_S2_Nr<Nr>_*_n<N>.npz` ≥ 15 — 기준 디렉터리에서 패턴이 정확히 15 (B32e4 24 파일 중 15, NR16B16e4 15; 후보 `.k0r*.npz` 는 접미사 불일치로 제외), (2) `done rc=0 job_g.: .*<--no-gbprime 명령>` in `~/t2_wtS/conf/logs/gpu_sched.log`; 학습 로그 `train_d2sx_<stem>_a1.log` 에 `stopped_by=diverged` 또는 rc≠0 → ALERT 만. 문서 서술과 일치. gpu_sched.log·NSCALE 학습 로그는 열지 않았다.
- 이름 일치 (스크립트 ↔ 코드): V1 stem `d2sx_N<N>_a1[_fb<k>]`·로그 `logs/train_d2sx_<tag>.log` (run_d2_sx :63–68, `--fallback` → `_fb{k}`), C6 `d2sx_NR16_N<N>_a1[_fb<k>]` (train_nr16 :54–58), D1 `ckpt/sx_N<N>_D1[_fb<k>].pt`·`logs/train_sx_N<N>_D1[_fb<k>].log` (run_samplecx :22–24) — prep :121·:143 의 `done(basename[:-3])` 와 §5 'D1 형제' 행의 로그 이름이 맞다. `--no-gbprime` → `sys.exit(0)` (run_d2_sx :79–80) 확인 (드래프터 미결 2 의 사실 관계).
- M2 (S_N 개수 문장) 문안이 검토 문안 그대로 §2.2 끝에 있고, (b) "'통과' (C6 의 (i) 에 해당)", (a) §3 머리말 '동결 전 확인' (2·3·4·5·6·16; 17 제외 — 17 은 ΣF/ΔR 이라 BLER 전용, 제외가 맞다), (c) 4차 bullet 의 정정 문장, 검토 표 4차 행 (반드시 3 → 2 + 결정 1, 권고 8 중 6 = (a)–(f), (g) 생략) 과 DECISIONS 동결 줄의 '4차 주 세션 결정 1 건' 이 서로 맞다. 구간 규칙 문구가 §5 체크포인트·D1 형제, §1 수용 (c)·보고 전용·학습 실패·자격·실행 스크립트, 예측 5 의 9 자리에 같은 뜻으로 들어 있다.
- 주 세션 결정 (강제 Q-K 우선, 늦음은 F1 사유 아님·단일 S5, F1 때 1.28e6 몫 미채점 + 예측 5 'F1 미발동' 채점, integ4-M1 구간 규칙) 은 재론하지 않았고 현재 문안이 그 결정과 어긋나는 곳은 없다. 단일 S5 (:217–219·:261), FALLBACK⇔PT B128e4 (:223–225), 14 필드·격자·gate·K2 조건 (:240–249), K8 run 1 조건 (:255–256), raw 존재/`--resume` (:257–259), HEAD 불변 (:269) 은 라운드 4·5 와 같은 코드 (diff) 라 다시 돌리지 않았다.
- 열지 않은 것: NSCALE 학습 로그 (`logs/train_d2sx_N640000_a1.log` 등)·적합 npz·적합 로그·`samplecx.csv` 새 행·`gpu_sched.log`·`~/t2_wtS` 의 어떤 파일·`*NR32_N160000_a3_fb3*`. 열람: 기준 학습 로그 3 개 + C6 a1·fb3 로그의 `# =====`·`# done` 줄 (grep), `score.py` :953–958·:1030–1037, `run_d2_sx.py` :40–100, `train_nr16.py`·`run_samplecx.py` 이름 줄, `10_SPEC_stageC.md` §3d :305–320, `logs/nscale/gbp_watch.sh`, 기준 fits 디렉터리 파일 수. GPU·BLER·커밋·삭제 없음; 스크래치는 `nscale_reg/r7/` 에 남겼다.

