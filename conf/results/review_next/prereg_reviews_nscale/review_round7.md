# NSCALE 등록 검토 원문 — 라운드 7 (워크플로 wf_64582bcf-e71; 작성자 Opus 5.5, 검토자 Fable 5.1 두 관점)

## 작성자 보고

라운드 7 반영을 마쳤습니다. 문서는 v5 → v6 으로 올렸습니다. 커밋, GPU, BLER, 삭제 명령은 쓰지 않았고, 시각은 `{{NOW}}` 그대로 두었습니다. `bash -n` 은 두 스크립트 모두 통과했고, 재실행한 하네스는 전부 기대대로 나왔습니다.

**바꾼 파일** (반영 전 백업: `nscale_reg/r10/{NSCALE_v5_pre_r7.md, run_nscale_pre_r7.sh}`)
- `/home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md` (v6)
- `/home/HTJ/t2/conf/code/run_nscale.sh`: `prep` 블록과 머리말 주석 한 줄만 바꿨습니다. eval 쪽은 그대로입니다.
- `/home/HTJ/t2/conf/code/nscale_gbp_watch.sh`: 읽기만 했고 바이트 동일합니다.

**(1) 감시 v2 반영 (stats-fair r6 M1 = integ6-M1)**
- **§1 학습 실패 행**: '재개는 작업 하나만' 문안을 하나의 재개·GB′ 규칙으로 바꿨습니다.
  - 중단되면 주 세션이 `--no-gbprime` 재개 작업 **하나**를 넣습니다. 넣기 전에 그 stem 의 작업이 `gpuq.txt` 에도 없고 실행 중도 아님을 확인해 §5 에 적습니다.
  - 감시는 그 재개 자신의 `# done … aborted=False` 가 로그의 마지막 `# done` 이 된 뒤에 GB′ 를 넣습니다.
  - 감시는 중단된 실행에는 GB′ 를 넣지 않습니다. 그 stem 의 작업이 큐에 있거나 도는 동안에도 넣지 않습니다.
  - 발산이나 rc ≠ 0 이면 주 세션이 §3d 또는 재실행을 마친 뒤 §4.1 명령으로 GB′ 를 직접 넣습니다 (로그 `logs/nscale/gbp_<T>.log`).
- **§4.1 GB′ 행**: 감시 설명을 v2 의 큐 조건 (a)–(d), NOTE, ALERT 로 다시 썼습니다. 감시 GB′ 가 중단 학습을 이어 마친다는 문안은 지웠습니다.
- **§1 실행 위치·커밋 행**: 동결 커밋 목록에 `code/nscale_gbp_watch.sh` 를 넣었습니다. 지금 추적되지 않은 파일이라, 빠지면 eval 전제의 conf/code 청결 검사가 걸립니다.
- 같은 내용을 §1 실행 스크립트 행, DECISIONS 행, §5 §3d 행에도 반영했습니다.
- 머리말에는 검토 표 6차 행, "6차 적대적 검토 반영" bullet, 그리고 5차 bullet (r5 M2) 과 4차 bullet (권고 (e)) 에 6차 주석을 달았습니다.

**(2) 권고**
- **(a) 줄 번호**: 현재 파일에서 확인했습니다. score.py :1031–1032, `_already_stopped` :737–747, run_d2_sx.py :79–80, train_nr16.py :68–69.
  - 5차 bullet 의 주장 문장은 제자리에서 고치고 주석을 달았습니다.
  - 5차 열람 줄의 범위 (:735–746) 는 실제로 읽은 범위라 그대로 두고, 함수 위치만 덧붙였습니다.
- **(b) `prep`**: attempt 1 다음에 모든 `ckpt/<stem>_fb*.pt` stem 마다 identity, `best.epoch == last.best_epoch`, `training:` 구간 줄을 `[§3d <stem>]` 머리로 찍습니다. attempt 1 출력과 DRAFT 는 바뀌지 않습니다.
- **(c)–(f)**: 지정 문안 그대로 넣었습니다. (e) 의 스크립트 줄은 편집 뒤 :248 입니다. (f) 는 5차 stats-fair 권고 1 에서 온 것이라고 명시했습니다.
- **생략**: integ6 권고 4. 감시 v2 에서는 감시가 중단 실행에 GB′ 를 넣지 않으므로 그 경우가 생기지 않습니다.

**확인 (`nscale_reg/r10/`)**
- **`prep`**:
  - fb stem 이 없는 새 거울: 옛 블록 출력과 바이트 동일하고, 라운드 6 출력 (`r6/t_prep_r5_single.txt`) 과도 바이트 동일합니다.
  - 가짜 fb stem (`d2sx_N320000_a1_fb2`): 옛 출력에 `[§3d …]` 네 줄만 더해졌습니다.
  - 실제 선례 C6B16e4 a1 stem (attempt 1 은 diverged): fb2 (best `c050d611b2c714a6`) 와 fb3 (로그는 머리말만) 의 여덟 줄이 더해졌습니다.
- **`done()`**: 라운드 6 과 동일합니다. A/B/C 와 기준 로그 3 개 assert 를 통과했습니다. fb stem 도 확인했습니다: 가짜 fb2 는 학습 구간 2, GB′ 구간 1, 학습 초 9100.0 s 이고, 선례 fb3 는 죽은 구간 1 입니다.
- **eval 쪽**: 아래 출력이 라운드 8 과 바이트 동일합니다 (TL 은 디렉터리 경로가 든 첫 줄만 다름).
  - 전제 9 + 10 경우
  - `qk`/`why` 6·6 경우
  - TL 13 경우
- **단일 S5**: 8 경우에서 PASS 4·ABORT 4 가 라운드 8 과 같은 자리에 나왔습니다.
- **감시 v2 별도 시험**: 가짜 트리 3 개에서 `ONESHOT=1` 과 가짜 `pgrep` 으로 돌렸습니다. 결과가 §4.1 문안과 일치합니다.
  - 중단 → NOTE, 넣지 않음
  - 큐에 그 stem 작업이 있거나 실행 중 → 넣지 않음
  - 발산, `rc=1` → 각각 ALERT
  - 적합 14 개 → 대기
  - 재개 뒤 `aborted=False` → 넣음
  - `gbp_<T>.log` 있음 → 건너뜀

**주 세션이 알아야 할 것**
1. §4.1 에 넣은 "감시 시험: 주 세션 가짜 트리 (`gbpt/`) 통과 1–5" 는 작업 지시에 적힌 문구를 옮긴 것입니다. `gbpt/` 에는 마지막 패스 로그만 남아 있어서 1–5 를 하나씩 확인하지는 못했습니다.
2. `# done` 줄도 rc ≠ 0 줄도 없이 끝난 실행 (스케줄러 자체가 죽은 경우) 은 감시가 로그를 남기지 않고 계속 기다립니다. §1 에는 "중단과 같다" 로 적었지만, 이 경우는 주 세션이 직접 알아채야 합니다.

## 검토 — 관점 stats-fair

### must

### should
- §1 학습 실패 행 (:140) 의 "(§0.6 의 학습 명령 그대로; …)" 에 한 절: "감시 (c) 는 줄에 부분 문자열 `code/run_d2_sx.py --ntrain <N′> ` / `code/train_nr16.py --nr 16 --ntrain 640000 ` 이 있을 때만 그 stem 의 작업으로 보므로 플래그 순서를 바꾸지 않는다 (`--ntrain` 이 스크립트 이름 바로 뒤)". 근거: 가짜 트리 `nscale_reg/r11rev/t3` — 재개 줄을 `run_d2_sx.py --no-gbprime --ntrain 640000` 순서로 `gpuq.txt` 에 두면 감시 v2 가 적합 15 + aborted=False 에서 GB′ 를 넣는다 (`t4` 의 `--ntrain 640000 --no-gbprime` 순서는 막힘). §4.1 (c) 에는 부분 문자열이 있으나 §1 의 재개 지시에는 의존성이 적혀 있지 않다.
- §1 학습 실패 행의 "재실행 (rc ≠ 0)" 을 "같은 명령 재투입 (= 재개; run_d2_sx.py :71·train_nr16.py :62 의 `resume=True` 라 ckpt 에서 이어지고, ckpt 는 지우지 않는다 — 죽은 구간은 §5 구간 규칙의 '하한')" 으로. 지금 어휘는 GB′ '재실행' (no-epoch) 과 겹쳐 처음부터 다시 돈다는 읽기가 남는다.
- §4.1 GB′ 행의 "감시 시험: 주 세션 가짜 트리 (스크래치 `gbpt/`) 통과 1–5" 는 `gbpt/logs/nscale/gbp_watch.log` 에 마지막 패스 (skip 1·queued 2·DONE) 만 남아 1–5 를 확인할 수 없다 (드래프터도 보고). "주 세션 보고: 가짜 트리 `gbpt/` 패스 1–5 (마지막 패스 로그만 남음); 독립 시험 `nscale_reg/r10/wt/` 3 트리 + 7차 검토 `r11rev/` 5 트리 (ONESHOT·가짜 pgrep) 가 (a)–(d)·NOTE·ALERT 와 일치" 로 출처를 적는다.
- 재개 명령을 run_nscale_gpu.sh `run()` 형식 그대로 넣으면 `> logs/nscale/v1_d2_n640000.log` 가 첫 실행의 stdout (`[d2sx] stopped_by=… aborted=…` 줄) 을 덮어쓴다 (훈련 로그 `logs/train_*.log` 는 append 라 기록은 무사). §1 에 "재개의 stdout 로그 이름은 `v1_<…>_r<k>.log`" 한 절이면 §5 전사에 두 실행의 stdout 이 남는다.
- `code/nscale_gbp_watch.sh` 가 동결 커밋에 들어가면 eval 전제 (:218, :225–226) 의 conf/code 청결·diff 검사 대상이 된다 — 동결 뒤 감시를 고치면 §5 커밋이 FREEZE 와 달라져 eval 이 ABORT 한다 (새 동결 = 사용자 승인 + DECISIONS). §1 실행 위치·커밋 행에 "감시 수정도 코드 변경이다" 한 절을 두어 주 세션이 동결 전에 끝내도록 한다.
- 감시의 NOTE 는 태그당 한 번 (`said[$t]`) 이라 재개가 다시 중단되면 둘째 NOTE 가 없다 — §4.1 "NOTE 만 남기고 기다린다" 에 "(태그당 한 번)" 을 붙이면 §5 §3d 행의 'NOTE 줄' 전사와 어긋나지 않는다.

### verified
- round-6 must (stats-fair r6 M1 = integ6-M1) 해소: `code/nscale_gbp_watch.sh` v2 가 드래프터 열람본 `nscale_reg/r10/watch_v2_read.sh` 와 바이트 동일 (cmp); 큐 조건 :37 = 적합 15 (:28 glob) + 마지막 `# done` aborted=False (:29) + `busy` 비어 있음 (:30 `gpuq.txt` grep -F + pgrep -f STEM) + `gbp_<T>.log` 없음 (:36); aborted=True → NOTE·대기 (:33–35), diverged (:31)·rc≠0 (:32) → ALERT·drop. §1 학습 실패 행 (:140)·§4.1 GB′ 행 (:267) 의 서술이 이 동작과 일치하며 '감시 GB′ 가 중단 학습을 이어 마친다' 문안은 없다.
- 감시 ↔ 스케줄러 계약 (`~/t2_wtS/conf/code/gpu_sched.sh` 코드만 열람): `take()` :28 이 `flock $Q.lock sed -i` 로 디스패치된 줄을 지우고, 감시의 append (:39) 도 같은 `gpuq.txt.lock` → (c) 의 gpuq grep 이 끝난 학습 줄에 영구히 걸리지 않고 append 가 유실되지 않는다; `launch` :20 이 `done rc=$rc job_g<g>: <cmd>` 를 큐 줄의 전체 명령으로 쓰므로 TR 정규식 (:32) 이 맞는다; run_nscale_gpu.sh :16·:23–25 의 학습 줄 `env -C $M $P code/run_d2_sx.py --ntrain 640000 --no-gbprime > $LG/v1_d2_n640000.log 2>&1` 이 STEM·TR 부분 문자열을 품는다.
- 감시 v2 독립 시험 (`nscale_reg/r11rev/`, ONESHOT=1·PGREP=false, 가짜 트리 5): t1 aborted=True + `done rc=137 … --no-gbprime` → ALERT rc!=0 (rc 가 NOTE 보다 우선, 넣지 않음); t2 `# done` 없음 → 로그 없이 대기 (드래프터 보고 2 와 같음); t4 정확한 재개 줄이 gpuq 에 있음 → 넣지 않음; t5 무관한 `--ntrain 6400000` rc=0 줄 → 오경보 없이 정상 큐; t3 플래그 순서 바꾼 재개 줄 → 넣음 (→ 권고 1).
- 코드 인용: score.py `_already_stopped` :737–747 (diverged/patience/max_epochs/None), `# resume` 줄은 `pre` 참일 때만 (:955–958), `except KeyboardInterrupt` :1031–1032, `# done … aborted={aborted}` :1036; run_d2_sx.py :79–80 `if a.no_gbprime: sys.exit(0)`, train_nr16.py :68–69 `return 0`; 두 트레이너 모두 `resume=True` (:71, :62) → 같은 명령 재투입 = 재개. `# done … aborted=False` 상태의 ckpt 는 `_already_stopped` 가 항상 patience/max_epochs 를 돌려 GB′ 작업이 epoch 를 더 돌지 않는다 (sha 불변).
- `bash -n` 두 스크립트 통과. `diff nscale_reg/r10/run_nscale_pre_r7.sh code/run_nscale.sh` = 머리말 주석 2 줄 + `prep` fb 루프 (:123–131) 뿐 → eval 조각 (전제·TL awk :248·qk·why·단일 S5) 은 라운드 8 검증 그대로. `prep`: `t_prep_pm0_{old,new}.txt` cmp 동일; `t_prep_pm1_{old,new}.txt` diff = `[§3d d2sx_N320000_a1_fb2]` 4 줄 추가, C6 선례 diff = `[§3d …_fb2]`·`[§3d …_fb3]` 8 줄 추가 (fb2 best c050d611b2c714a6, fb3 구간 = 머리말만); 스크립트의 prep 블록이 시험본 `prep_new.py` 와 바이트 동일.
- 문서 v6: 권고 (a) 줄 번호 (:44 :1031–1032·:737–747, :46 정정 주석, :140), (b) §1 체크포인트 행 괄호 (:139)·실행 스크립트 행 (:154), (c) "1.6e5·3.2e5 는 PASS 레시피, 새 점은 §5 게이트대로" (:203), (d) C6 사유 괄호 (:203), (e) "학습 구간 (`# resume` 없는 구간) 들의 마지막 `# done`" (:154 = :248 awk), (f) '동결 전 확인' 채점 제외 (:236); 동결 커밋 목록에 `code/nscale_gbp_watch.sh` (:153, 추적되지 않은 파일 `??` 확인), DECISIONS 행 (:158), §5 §3d 행의 넣기 전 확인·gbp_watch.log 줄 (:296). 6차 반영 수 (반드시 2 → 병합 1, 권고 8 중 7 = (a)–(e) + (f), integ6 권고 4 생략) 가 r6 검토 두 건과 맞고, 생략 사유 (v2 는 aborted=True 에 넣지 않음) 는 :33–35 로 성립.
- 결정 사항 유지·재론 없음: Q-K 강제 > L⁰ (:199), 늦음은 F1 사유 아님·단일 S5 (:143, :153; 스크립트 :221–223), F1 때 1.28e6 몫 미채점·예측 5 'F1 미발동' (:235, :242), 구간 규칙 (:295, :140, :248). 시각 입력 없음 (HH:MM CDT/KST·'x CDT' 패턴 0), `{{NOW}}` 32 개; 옛 `logs/nscale/gbp_watch.sh` 는 이력 bullet 과 '첫 판 대체' 문구에만 (:38, :39, :46, :50, :267).
- 현황 (열거만): tmux `nsgbp` 세션 존재, `logs/nscale/gbp_watch.log` 는 `start` 3 줄 (queued·NOTE·ALERT 없음), `logs/nscale/gbp_watch_v1.sh.old` 존재. 열지 않은 것: NSCALE 학습 로그·적합 npz/로그·`gbp_<T>.log`·`samplecx.csv` 새 행·`~/t2_wtS/conf/logs/{gpuq.txt,gpu_sched.log}`·SEEDSNR 파일; GPU·BLER·커밋·삭제·tmux 조작 없음; 스크래치는 `nscale_reg/r11rev/` 에 남김.

## 검토 — 관점 integ

### must

### should
- §4.1 GB′ 행 끝의 "감시 시험: 주 세션 가짜 트리 (스크래치 `gbpt/`) 통과 1–5" 는 확인할 수 없는 주장이다 — `gbpt/` 에는 마지막 패스 (B64e4 skip · B128e4/NR16B64e4 queued · GBP_WATCH_DONE) 의 로그만 남아 있다. 동결 전에 다음으로 교체: "감시 시험: 6차 반영 확인의 가짜 트리 3 개 (`nscale_reg/r10/wt` p1–p3) 와 7차 검토자 하네스 (`nscale_reg/r11` c1–c8: 중단 → 재개 큐 → 재개 실행 중 (`# done` 이미 쓰인 경합 창 포함) → 완료 → queued → 감시 재시작 → 시작 뒤 skip; rc 정규식 (자기 학습 rc=0·D1 rc=137·GB′ `--tag` rc=1 은 ALERT 아님, `--no-gbprime` rc≠0 만 ALERT); 적합 14 + 후보 9 → 대기; 머리말만 → 무출력 대기; `drop` 의 B64e4/NR16B64e4 독립; 실제 `pgrep` 이 job_g 셸·python 둘을 잡음) — 출력은 `prereg_reviews_nscale/` 에 넣는다" (또는 주 세션이 1–5 각 패스의 `gbp_watch.log` 를 그 디렉터리에 둔다).
- §1 학습 실패 행의 수동 GB′ (발산 뒤 §3d, rc ≠ 0 뒤 재실행) 문장 "(넣기 전 같은 확인)" 에 감시 조건 (b) 와 같은 전제를 덧붙인다: "(넣기 전 같은 확인 + 그 stem 학습 로그의 학습 구간 마지막 `# done` 이 `aborted=False`·`stopped_by=diverged` 아님 — 감시 (b) 와 같은 조건; 아니면 GB′ 작업이 `_already_stopped` = None 으로 학습을 이어 돌아 GB′ 로그가 학습 구간이 된다)". 감시 v2 는 이 경로를 막지만 수동 경로는 막지 않으므로 integ6 권고 4 의 절은 수동 GB′ 경우로 한정해 §5 체크포인트 행에 한 줄 남겨 두는 것이 안전하다 ("수동 GB′ 가 미완 학습을 이어 마친 경우 그 구간은 `# resume` 없는 학습 구간, GB′ 구간 0, GB′ 증거는 `gbp_<T>.log`·수용 (h)").
- §1 학습 실패 행에 한 문장: "감시가 들고 있는 태그 (ALERT 로 버리지 않은 태그) 에는 주 세션이 GB′ 를 직접 넣지 않는다 — 재개 완료 뒤 120 s 안에 감시가 넣는다 (`gbp_watch.log` 의 queued 줄 확인)". 지금 문안은 수동 GB′ 를 발산·rc≠0 경우로만 암시해, 재개 완료 직후 주 세션이 먼저 넣으면 감시와 이중 큐 (둘 다 no-epoch 재개라 ckpt 는 무변이지만 `gbp_<T>.log` 가 `>` 로 덮이고 csv·npz 가 중복) 가 가능하다.
- §4.1 감시 서술에 두 사실을 괄호로: NOTE 는 감시 프로세스당 태그마다 한 번만 찍히고 (`said`; 재개가 다시 중단되어도 새 NOTE 없음), `# done` 없이 끝난 실행 (tmux kill-session: rc 줄도 없음) 에는 아무 줄도 찍지 않는다 — §5 §3d 행의 'gbp_watch.log 의 queued·NOTE·ALERT 줄' 전사가 비어 있어도 그 경우가 없었다는 뜻이 아니다.
- 동결 커밋 전에 `code/nscale_gbp_watch.sh` 를 한 글자라도 바꾸면 tmux `nsgbp` (pid 3247507, 04:02:04 KST 시작, 바이트 = 현재 파일) 를 다시 띄우고 §4.1 에 적는다; 동결 때 §4.1 관측에 실행 중 스크립트의 `sha256sum` 을 함께 적으면 '실행 중 = 커밋본' 이 기록된다.

### verified
- 감시 v2 를 가짜 트리에서 직접 돌림 (`nscale_reg/r11/`, `ONESHOT=1`, 감시 파일은 읽기만): c1 순서 — B64e4 중단 (aborted=True) → NOTE·안 넣음, B128e4·NR16B64e4 queued; 재개 줄이 gpuq → 안 넣음 (NOTE 반복 없음); 재개 실행 중 (가짜 pgrep) + 새 머리말 → 안 넣음; 재개가 `# done aborted=False` 를 썼으나 프로세스 생존 (경합 창) → 안 넣음 (busy); 종료 뒤 → queued B64e4; GB′ 줄이 gpuq 에 있는 채 감시 재시작 → 안 넣음·DONE 아님; 시작 뒤 (gbp 로그 존재) → skip·GBP_WATCH_DONE. c3f rc 정규식 — `done rc=0` 자기 학습, `rc=137 run_samplecx.py 640000`, `rc=1 … --tag B64e4` (GB′ 실패) 는 ALERT 아님 → 셋 queued; `rc=137/10/1 … --no-gbprime[ --fallback 2]` → 셋 ALERT. c4 머리말만 (kill-session) → 무출력 대기, 발산 → ALERT. c5f 병합 14 + 후보 `.k0r*` 9 → 대기 (글롭 14). c6 `drop B64e4` 가 NR16B64e4 를 지우지 않음 (`grep -vx`). c8 실제 `pgrep` + argv 가 stem 문자열인 가짜 프로세스 → 안 넣음; c7 실제 pgrep 에 현재 도는 세 학습 (job_g 셸 `bash -c cd …; CUDA_VISIBLE_DEVICES=4 …` 와 python 둘 다 잡힘) → 셋 다 안 넣음. §4.1 (a)–(d)·NOTE·ALERT 서술과 전부 일치.
- 감시 ↔ 스케줄러: `~/t2_wtS/conf/code/gpu_sched.sh` `take` 가 띄울 때 그 줄을 `sed -i` 로 지우고 (대기 = gpuq.txt, 실행 = tmux job_g 셸 cmdline 에 명령 전문) → busy 검사가 대기·실행을 모두 덮는다; 종료 줄 `done rc=$rc job_g<g>: <cmd>` 가 TR 정규식에 맞음; 같은 `gpuq.txt.lock`. 감시 프로세스는 v2 하나 (pid 3247507 `bash /home/HTJ/t2/conf/code/nscale_gbp_watch.sh`, 04:02:04 KST), v1 은 돌지 않고 파일은 `gbp_watch_v1.sh.old`; `gbp_watch.log` = start 3 줄 (queued·NOTE·ALERT 없음) = 6차 bullet 서술. tmux 는 이름만 열거 (gpusched·job_g0–5·nsgbp·seedsnr·dev).
- 이름·플래그: run_d2_sx.py :39 `--tag` (runner._init → gmm_fits_D2_<tag>), :43 `--no-gbprime`, :44 `--fallback`, :63–68 stem `d2sx_N<N>_a1[_fb<k>]`·로그 `logs/train_d2sx_<tag>.log`; train_nr16.py :33 `--nr`, :45 `--no-gbprime`, :46 `--fits-tag`, :54–58 `d2sx_NR16_N<N>_a1[_fb<k>]` → 감시 CMD/TL/TR/STEM, run_nscale.sh NEW stem·`logs/train_$3.log`, §4.1 세 명령이 모두 맞다. run_nscale_gpu.sh: 적합 디렉터리 `gmm_fits_D2_{B64e4,B128e4,NR16B64e4,K8B64e4}`, 로그 `logs/nscale/fit_<T>_*`·`v1_*`·`bpass_*`, 84 작업 (8 + 24×3 + 4) = §0.6; `arms.D2_KS` 에 8192 포함 → K8 별도 디렉터리 서술 맞음. §1·5차·6차 bullet 의 줄 번호: score.py `_already_stopped` :737–747, KeyboardInterrupt :1031–1032, `# resume` :955–958, `# done` :1036–1037, 머리말 :919; run_d2_sx :79–80; train_nr16 :68–69 — 전부 현재 파일과 일치.
- 스크립트: `diff r10/run_nscale_pre_r7.sh code/run_nscale.sh` = 머리말 주석 1 줄 + `prep` fb 루프 (:123–131) 뿐; r8 백업 대비 = 그 + TL 두 줄 (:248–249); `bash -n` 둘 다 통과; 감시 파일은 r10 열람 사본과 바이트 동일. `prep`: 현재 블록 (:56–179 추출) 을 드래프터 거울 `pm1` 에 C6B16e4 a1 stem 으로 다시 돌림 → 드래프터 `t_prep_pm1_new_C6a1.txt` 와 바이트 동일 (`[§3d …_fb2]` best c050d611b2c714a6·patience 1704, `[§3d …_fb3]` 머리말만 — 여덟 줄); `pm0` old == new; `pm1` old/new 차이는 `[§3d d2sx_N320000_a1_fb2]` 네 줄만. 선례 로그 grep (BLER 아님): a1 :1076 diverged, fb2 :1712 patience, fb3 :2 머리말만, B32e4 :994/:996/:1002–1003.
- eval 쪽 (바뀌지 않음): r10/h 의 추출 조각 6 개 (guard_pre·guard_write·pre_fb·pre_pt 27 줄·qk_fn·okpt_fn) 가 현재 스크립트에 그대로 있음; `t_pre2.sh`·`t_pre.sh`·`t_qk_why.sh` 재실행 출력이 라운드 8 과 바이트 동일, 단일 S5 `t_single.sh` PASS 4·ABORT 4 같은 자리 (차이는 기존 repo2 재사용으로 생긴 `git status` 배너뿐). frontier_ci.py :364–373: `--extrap - - --ck - -` 허용, k2 둘 None 이면 R+ 줄 없음 → §1 Q-K 의 '외삽이 없는 파일은 `R1 - R2` 줄' 규칙이 새 끝 내부일 때의 실행 (b) 를 덮는다. 두 작업이 한 ckpt 를 쓰는 경로: 감시는 마지막 `# done` 이 aborted=False 일 때만 + stem 작업 부재 + gbp 로그 부재에서 한 번 넣고, 재개 중에는 마지막 줄이 aborted=True 라 넣지 않으며, 발산·rc≠0 은 버린다 — 문서 §1 규칙 (재개 하나·넣기 전 확인·수동 GB′ 는 버린 태그만) 과 합쳐 경로가 닫힘 (남은 틈은 should 2·3 의 수동 GB′ 전제·이중 큐).
- 문서: `{{NOW}}` 32 개, HH:MM CDT/KST 입력 없음; `git status --porcelain conf/code` = `?? run_nscale.sh`, `?? nscale_gbp_watch.sh` 둘뿐 (동결 커밋 목록과 일치, Demo 청결). 열지 않은 것: NSCALE 학습 로그·체크포인트·적합 npz/로그·`gbp_<T>.log`·`samplecx.csv` 새 행, `~/t2_wtS` 의 코드 외 파일 (gpu_sched.sh 만 읽음), SEEDSNR 파일. GPU·BLER·커밋·삭제 명령 없음; tmux 는 `tmux ls` 열거만; 스크래치는 `nscale_reg/r11/` 에 남김.

