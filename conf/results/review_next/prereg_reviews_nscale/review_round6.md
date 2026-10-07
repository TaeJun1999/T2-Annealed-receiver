# NSCALE 등록 검토 원문 — 라운드 6 (워크플로 wf_1d727603-a0f; 작성자 Opus 5.5, 검토자 Fable 5.1 두 관점)

## 작성자 보고

라운드 6 반영 완료 (커밋 없음, GPU·BLER 미사용, 삭제 명령 없음, 시각은 `{{NOW}}` 유지).

**바뀐 파일**
- `/home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md` (v4 → v5)
- `/home/HTJ/t2/conf/code/run_nscale.sh` (eval 전제 NEW 루프의 :243 뒤에 검토 문안 그대로 2 줄 추가. `bash -n` 통과, diff 는 이 추가 2 줄뿐)
- 반영 전 백업: `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/nscale_reg/r8/{NSCALE_v4_pre_r6.md, run_nscale_pre_r6.sh}`

**반영 내용 (세 건 모두 검토 문안 그대로)**
- **stats-fair r5 M1**: §2.2 S_N 끝 문장의 사유 괄호를 `PT <tag> -`·수용 실패·통과 못함 셋으로 줄였다. "**D1 게이트 FAIL 은 '통과 아님' 의 사유가 아니다**" 문장을 넣었다. 4차 bullet 의 r4 M2 항목 끝에 5차 주석을 달았다.
- **stats-fair r5 M2**: §1 학습 실패 행에 "**재개는 작업 하나만**" 규칙을 넣었다. §4.1 GB′ 재실행 행에 감시가 `aborted` 를 보지 않는다는 괄호를 넣었다. 4차 bullet 의 권고 (e) 끝에 5차 주석을 달았다. 인용한 줄은 직접 확인했다: score.py :1030–1031·:735–746, run_d2_sx.py :77–80, train_nr16.py :68–69.
- **integ5-M1**:
  - 스크립트에 S5 stem 학습 로그 검사를 넣었다. 마지막 학습 구간의 `# done` 이 `aborted=False` 이고 diverged 가 아니어야 하며, 줄이 없으면 ABORT 한다.
  - 문서는 §1 실행 스크립트 행의 전제 목록과 §1 체크포인트·평가 가중치 행의 괄호를 바꿨다.
- **머리말**: 제목과 상태 줄을 v5 로 올렸다. 검토 라운드 표에 5차 행을 넣었다. "5차 적대적 검토 반영" bullet 을 새로 달았다 (id → 바뀐 곳, 열람, 확인).

**검사 결과 (`nscale_reg/r8/`)**
- **새 검사 2 줄 단독 (`t_tl.out`)**:
  - 가짜 로그 8 개: 정상 + GB′, 중단 → 재개 → GB′, 죽은 구간 + 재개는 PASS. 머리말만, interrupted 만, diverged, diverged + GB′, 로그 없음은 ABORT.
  - 기준·선례 로그 5 개: B32e4 a1, NR16B16e4 fb2, D1 3.2e5 는 PASS. C6B16e4 시행 1 (diverged, :1076) 과 시행 3 (머리말만) 은 ABORT.
- **eval 전제**:
  - 기존 9 경우는 라운드 6 출력과 바이트 동일하다 (`t_pre_A-I.out`).
  - 새 9 경우는 모두 기대대로다 (`t_pre2.out`). `PT B64e4 -` 에 로그가 없어도 PASS 이고, NR16B64e4 의 `_fb2` 로그가 diverged 면 ABORT 다.
- **qk·why**: 출력이 라운드 6 과 바이트 동일하다.
- **단일 S5 (8 경우)**: PASS 4·ABORT 4 가 같은 자리에 나온다.
- **prep**: 블록이 라운드 6 추출본과 바이트 동일하다.

**주 세션이 정할 것**
1. **감시 스크립트로 인한 이중 기록 위험이 남아 있다.** 새 §1 문안은 "적합 15 개가 미완이면 재개를 넣고, 끝난 뒤 주 세션이 GB′ 를 직접 넣는다" 이다. 그런데 `logs/nscale/gbp_watch.sh` :18 의 조건은 `gpu_sched.log` 에서 `done rc=0 … --no-gbprime` 줄을 찾는 grep 이다. 중단된 실행이 남긴 이 rc=0 줄은 계속 남아 있다.
   - 그래서 재개가 도는 동안 적합 15 개가 갖춰지면, 감시가 GB′ 를 자동으로 큐에 넣는다.
   - 그러면 두 작업이 같은 ckpt 를 동시에 쓰게 되고, 이것이 바로 새 규칙이 막으려던 상황이다.
   - 감시 스크립트의 가드는 반영 범위 밖이라 고치지 않았다. 그 태그의 감시를 멈추거나 감시 쪽에 가드를 넣을지 정해야 한다.
2. 검토가 인용한 감시 줄 번호 :14–17 은 현재 파일에서 :15–21 이다. 바뀐 문서 문안에는 감시 줄 번호가 없어 영향은 없고, 5차 bullet 에 이 사실을 적어 두었다.

## 검토 — 관점 stats-fair

### must
- **stats-fair r6 M1** (NEXT_EXPERIMENTS_NSCALE.md §1 '학습 실패' 행 (:133, 5차 r5 M2 로 들어온 '재개는 작업 하나만' 문장) · §4.1 GB′ 재실행 행 (:260 괄호))
  - 문제: 새 규칙의 둘째 분기가 막으려던 이중 기록을 그대로 남긴다. 문안: "그 GB′ 줄이 gpuq.txt 에 있거나 돌고 있으면 재개를 넣지 않는다; 없으면 (적합 15 개 미완 …) --no-gbprime 재개를 넣고 끝난 뒤 GB′ 를 주 세션이 직접 넣는다 … 넣기 전에 gpuq.txt 와 gpu_sched.log 에서 그 stem 의 작업이 없음을 확인". 확인은 넣는 시점 한 번뿐인데 감시 `logs/nscale/gbp_watch.sh` (tmux `nsgbp`, 지금 돌고 있음 — `tmux ls` 1 건) 의 큐 조건 :18 은 `[ n -ge 15 ] && grep -q "done rc=0 job_g.: .*<--no-gbprime 명령>" gpu_sched.log` 뿐이고 `gpuq.txt`·실행 중 프로세스를 보지 않는다. 중단된 실행 (KeyboardInterrupt → score.py :1031–1032 aborted=True, run_d2_sx.py :79–80 `sys.exit(0)`, train_nr16.py :68–69 `return 0`) 이 남긴 `done rc=0` 줄은 계속 남으므로, 주 세션이 규칙대로 재개를 넣은 뒤 그 재개가 도는 수 시간 안에 적합 15 개가 갖춰지면 감시가 GB′ (`run_d2_sx.py --ntrain N --tag T`, `--no-gbprime` 없음) 를 넣고, 그 작업은 `_already_stopped` = None (score.py :737–747) 이라 같은 `ckpt/<stem>{,_best}.pt`·`logs/train_<stem>.log` 에 학습을 이어 쓴다 → 두 프로세스가 같은 ckpt 를 번갈아 덮어쓰고 (append 로그는 줄 단위로 섞여 `# =====`·`# done` 이 둘씩 생김) eval 전제 :244 의 '학습 구간 마지막 `# done`' 은 어느 쪽 aborted=False 줄이든 통과시키므로 조용한 오기록이 된다. 드래프터 보고 '주 세션이 정할 것 1' 과 같은 경로이며, 문서가 '감시 쪽 가드는 범위 밖' 이라 둔 채 규칙만 등록되면 동결 뒤 고칠 수 없다.
  - 수정: :133 의 "그 GB′ 줄이 `gpuq.txt` 에 있거나 돌고 있으면 `--no-gbprime` 재개를 따로 넣지 않는다; 없으면 (적합 15 개 미완, 또는 rc ≠ 0 로 감시가 태그를 버림) `--no-gbprime` 재개를 넣고 끝난 뒤 GB′ 를 주 세션이 직접 넣는다. 같은 ckpt 를 두 작업이 동시에 쓰면 체크포인트·로그 구간이 섞여 §5 체크포인트 행의 구간 규칙이 복구되지 않는다 — 넣기 전에 `gpuq.txt` 와 `gpu_sched.log` 에서 그 stem 의 작업이 없음을 확인하고 §5 에 적는다." 를 다음으로 교체: "그 GB′ 줄이 `gpuq.txt` 에 있거나 돌고 있으면 `--no-gbprime` 재개를 따로 넣지 않는다 (그 GB′ 작업이 재개다); 없으면 (적합 15 개 미완, 또는 rc ≠ 0 로 감시가 태그를 버림) **먼저 감시를 멈춘 뒤** (`tmux kill-session -t nsgbp`; `gbp_watch.sh` 는 태그별 끄기가 없고 큐 조건 (:18) 이 `gpuq.txt`·실행 중 작업을 보지 않아, 재개가 도는 동안 적합 15 개가 갖춰지면 중단 실행이 남긴 `done rc=0 … --no-gbprime` 줄로 GB′ 를 넣어 두 작업이 같은 ckpt 를 쓴다) `--no-gbprime` 재개를 넣고, 끝난 뒤 (학습 구간 마지막 `# done` 이 `aborted=False`) GB′ 를 주 세션이 §4.1 의 명령으로 직접 넣는다. 감시를 멈춘 뒤에는 남은 모든 태그의 GB′ 도 주 세션이 같은 조건 (적합 15 개 + 학습 `# done` `aborted=False`·발산 아님) 으로 직접 넣고 감시를 다시 띄우지 않는다. 같은 ckpt 를 두 작업이 동시에 쓰면 체크포인트·로그 구간이 섞여 §5 체크포인트 행의 구간 규칙이 복구되지 않는다 — 넣기 전에 `gpuq.txt` 와 `gpu_sched.log` 에서 그 stem 의 작업이 없음과 감시 종료 (`gbp_watch.log` 마지막 줄·`tmux ls`) 를 확인하고 §5 에 적는다." :260 의 "rc ≠ 0 로 버려진 태그는 재개와 GB′ 를 모두 주 세션이 직접 넣는다)" 를 "rc ≠ 0 로 버려진 태그는 재개와 GB′ 를 모두 주 세션이 직접 넣는다; 재개를 넣어야 하는 경우에는 어느 분기든 감시를 먼저 멈춘다 — 감시는 재개가 도는 동안에도 조건이 차면 GB′ 를 넣는다, §1 학습 실패 행)" 로 교체. 주 세션이 대신 감시 쪽을 고치기로 하면 (`gbp_watch.sh` :18 조건 끝에 `&& ! grep -q "${TR[$t]}" $S/gpuq.txt && ! pgrep -f "${TR[$t]}" > /dev/null`, 재시작 뒤 `gbp_watch.log` 에 기록) 위 두 문안의 '감시를 멈춘다' 를 '감시가 그 stem 의 대기·실행 중 작업이 없을 때만 넣는다 (가드 :18)' 로 바꿔 적는다 — 둘 중 하나는 동결 전에 문서에 있어야 한다.

### should
- §2.2 S_N C2 전체 문장 틀 (:196) 의 고정 어구 "1.6e5 이상은 PASS 레시피" 는 새 점 게이트가 FAIL 이면 같은 문장 안의 '게이트 FAIL 인 새 점은 … 예산 축 측정 표기' 와 어긋난다 → "1.6e5·3.2e5 는 PASS 레시피, 새 점은 §5 게이트대로" 로.
- §2.2 S_N 끝 (:196) 의 '통과 아님' 사유 목록은 C2 어휘뿐이다 → 괄호 끝에 "(C6 의 (i) 아님 은 (ii)/(iii)/(iv) 라벨 그대로, `PT NR16B64e4 -`, 수용 실패)" 를 덧붙여 C6 개수 문장의 괄호도 한 읽기로.
- run_nscale.sh `prep` :126 은 `_fb*` ckpt 이름만 적고 그 로그는 내놓지 않아 §3d 가 쓰이면 §5 체크포인트 행의 '`prep` 출력 그대로' 가 attempt 1 (발산) 로그만 가리킨다 → :126 뒤에 `    for p in sorted(glob.glob(f'ckpt/{stem}_fb*.pt')):\n        if not p.endswith('_best.pt'): print(f"  other attempt {os.path.basename(p)}: training: {done(os.path.basename(p)[:-3])}")` 두 줄 (eval 전제 :244 가 S5 stem 로그를 따로 검사하므로 기록 편의 — 필수 아님).
- 인용 줄 번호: §1 :133 과 5차 bullet :43 의 'score.py :1030–1031 이 KeyboardInterrupt 를 잡고' 는 현재 파일에서 :1031–1032 (`except KeyboardInterrupt:` / `stopped, aborted = "interrupted", True`); :1030 은 `break` 다.

### verified
- 스크립트: `diff r8/run_nscale_pre_r6.sh code/run_nscale.sh` = :244–245 두 줄 추가뿐, `bash -n` 통과; 두 대상 파일은 미커밋 (`??`), 시각 패턴 (HH:MM CDT/KST, 'x CDT') 없음, `{{NOW}}` 31 개 유지.
- integ5-M1 검사 (:244–245) 를 기준·선례 로그 5 개에 직접 적용: `train_d2sx_N320000_a1` → :994 patience/aborted=False (:996 구간은 :1002 `# resume` 으로 제외), `…NR16_N160000_a1_fb2` → :1712 patience, `train_sx_N320000_D1` → :208 patience (PASS 셋); `…NR16_N160000_a1` → :1076 stopped_by=diverged, `…_a1_fb3` → 머리말만 (빈 TL) (ABORT 둘) = 드래프터 `r8/t_tl.out` 과 같음. `r8/t_pre_A-I.out` 은 `r6/t_pre.out` 과 cmp 동일; `r8/pre_pt.sh` 는 현재 :232–258 을 그대로 품는다 (diff 는 하네스 쪽 추가 줄만).
- 검사가 기대는 로그 형식: score.py :1036–1037 `# done : … stopped_by={stopped}, aborted={aborted} …` (리터럴 'aborted=False'·'stopped_by=diverged'), `# resume` 줄은 `_already_stopped` 가 참일 때만 (:954–958), KeyboardInterrupt → interrupted/aborted=True (:1031–1032), 재개 실행에 머리말 표시 없음 (:919–920) → '`# resume` 없는 `# =====` 구간 = 학습' 이 코드와 맞고 awk 가 그 규칙 그대로다. 로그·stem 이름: run_d2_sx.py :63–68 (`d2sx_N<N>_a<k>[_fb<j>]`, `logs/train_d2sx_<tag>.log`), train_nr16.py :54–58 → `logs/train_$3.log` (S5 stem, 정규식 `^$STEM(_fb[23])?$`) 이 맞는 파일. `PT <tag> -` 점은 :239 에서 먼저 건너뛴다 (t_pre2.out R).
- 학습 줄 규칙의 단일성: §1 :133 (§3d 판정 = 학습 구간 마지막 `# done`), §5 :288 (체크포인트 행), §5 :290 (D1 형제, 같은 규칙), §3 :235 (예측 5 채점 줄), eval :244 — 같은 한 규칙. §1 :132·:147 의 전제 설명이 :244–245 와 일치.
- stats-fair r5 M1 (§2.2 :196): 사유 괄호 = `PT <tag> -`·수용 실패 (표 B 없음)·통과 못함; 'D1 게이트 FAIL 은 통과 아님의 사유가 아니다', k·S_N 은 표 B 출력으로만; 셀별 n·k (C2 6/5 · C6 3) 와 기준점 몫 (C2 4·C6 2, POWERED·3/3) 고정 — r4 M2 반영 유지, 4차 bullet :36 에 5차 주석.
- stats-fair r5 M2: §1 :133 '재개는 작업 하나만' 과 §4.1 :260 괄호가 있고 인용 (run_d2_sx.py :79–80 `sys.exit(0)`, train_nr16.py :68–69 `return 0`, `_already_stopped` :737–747) 은 맞다 — 다만 둘째 분기의 빈틈이 M1. `gbp_watch.sh` 직접 열람: :15 개수 = glob `fit_S2_Nr<nr>_*_n<N>.npz` (B32e4 디렉터리 24 파일 중 15, NR16B16e4 15 — `.k0r*` 후보 제외 맞음), :16 diverged → 버림, :18 n ≥ 15 && `done rc=0 job_g.: .*<--no-gbprime>` → 큐 (태그마다 한 번 = `left` 제거), :21 rc ≠ 0 → 버림; `gpuq.txt`·실행 중 검사 없음. 드래프터의 줄 번호 정정 (:15–21, 큐 :18, rc≠0 :21) 맞음. tmux `nsgbp` 세션 존재 (`tmux ls`, 열거만).
- 4차 반드시 유지: `done()` :94–98 이 `# =====` 머리말을 내놓고 §5 :288 구간 규칙·§1 수용 (c) :145·보고 전용 :144 가 같은 규칙; `k2set`·K8 줄 검사 (:255–258)·단일 S5 (:217–219, :263)·FALLBACK ⇔ `PT B128e4 -` (:223–225) 는 바뀌지 않았다 (pre_pt.sh 대조·t_pre_A-I 동일).
- 머리말: 검토 표 5차 행 (:11), 5차 bullet (:41–46; id → 바뀐 곳·열람·확인) 있음. 주 세션 결정 3 건 (Q-K 강제 우선·늦음은 F1 사유 아님·F1 때 1.28e6 몫 미채점, 예측 5 'F1 미발동' 은 채점) 은 §1·§2.2·§3 머리말에 그대로 — 재론 없음.
- 열람 범위: 기준·선례 학습 로그 5 개의 `# =====`·`# done`·`# resume`·`# DEVICE` 줄 (grep), `code/score.py`·`run_d2_sx.py`·`train_nr16.py`, `logs/nscale/gbp_watch.sh`, 기준 fits 디렉터리 파일 이름, 드래프터 r8 하네스·출력. NSCALE 학습 로그·적합 npz/로그·`samplecx.csv` 새 행·`gpu_sched.log`·`~/t2_wtS` 파일은 열지 않았고 GPU·BLER·커밋·삭제·tmux 조작 없음.

## 검토 — 관점 integ

### must
- **integ6-M1** (NEXT_EXPERIMENTS_NSCALE.md §1 '학습 실패' 행 (:133) 의 '재개는 작업 하나만' 규칙 (5차 stats-fair r5 M2 반영 문안) · §4.1 GB′ 재실행 행 (:260) 괄호 · 머리말 5차 bullet (:43) 주석)
  - 문제: 5차 반영 문안이 막으려던 이중 쓰기가 그 문안 자체의 '없으면' 분기로 다시 열린다. 규칙은 "그 GB′ 줄이 gpuq.txt 에 있거나 돌고 있으면 재개를 넣지 않는다; 없으면 (적합 15 개 미완, 또는 rc ≠ 0) --no-gbprime 재개를 넣고 끝난 뒤 GB′ 를 주 세션이 직접 넣는다" 인데, 감시 `logs/nscale/gbp_watch.sh` :18 의 큐 조건은 `gpu_sched.log` 의 `done rc=0 job_g.: .*<--no-gbprime 명령>` 줄 (gpu_sched.sh :20 이 세션 끝에 쓴다) + 적합 15 개이고, 그 태그는 큐에 넣거나 ALERT 할 때까지 `left` 에 남는다 (:17, :20, :21). 구체 경로: V1 학습이 SIGINT 로 중단 (score.py :1031–1032 → aborted=True, rc=0; 적합은 아직 15 개 미완) → 주 세션이 규칙대로 `--no-gbprime` 재개를 넣는다 (그 시점 GB′ 줄 없음, 확인 통과) → 재개가 몇 시간 도는 동안 kron 병합이 끝나 적합 15 개가 갖춰진다 → 감시가 중단 실행이 남긴 rc=0 줄을 보고 GB′ 작업 (우선순위 90) 을 넣고 스케줄러가 다른 GPU 에서 띄운다 → GB′ 작업은 `_already_stopped` None (score.py :737–747) 이라 같은 `ckpt/<stem>{,_best}.pt`·`logs/train_<stem>.log` 에 학습을 이어 쓴다 — 두 프로세스가 같은 체크포인트·로그를 동시에 쓰는 상태, 문안이 금지한 바로 그 경우. 적합 15 개가 이미 있는 중단에서도 감시 주기 120 s 안에 주 세션이 먼저 넣으면 같은 경합이다. 마지막에 끝난 쪽이 `# done … aborted=False` 를 남기므로 eval 전제 (:244–245 TL 검사·:242–243 sha 검사) 는 통과하고, 평가되는 가중치는 동결 레시피가 아니라 두 학습의 교차 쓰기 산물이 된다 (재현 불가·§5 체크포인트 행 복구 불가). 감시는 현재 살아 있다 (tmux `nsgbp`, `gbp_watch.log` 에 `start` 줄 둘뿐 — queued·ALERT 없음) 이라 세 태그 모두 이 경로 위에 있다. 감시 스크립트 수정은 주 세션 몫이지만, 문서 쪽 규칙만으로 경로를 닫을 수 있고 지금 문안은 닫지 않는다.
  - 수정: §1 학습 실패 행 (:133) 에서 다음 두 문장을 — "그 GB′ 줄이 `gpuq.txt` 에 있거나 돌고 있으면 `--no-gbprime` 재개를 따로 넣지 않는다; 없으면 (적합 15 개 미완, 또는 rc ≠ 0 로 감시가 태그를 버림) `--no-gbprime` 재개를 넣고 끝난 뒤 GB′ 를 주 세션이 직접 넣는다." — 다음으로 교체: "감시의 큐 조건 (`gbp_watch.sh` :18) 은 `gpu_sched.log` 의 `done rc=0 … <그 태그의 --no-gbprime 명령>` 줄 + 적합 15 개이며 중단된 실행이 남긴 그 rc=0 줄은 계속 남아 있으므로, 재개 여부는 그 줄로 정한다. (1) `gpu_sched.log` 에 그 태그의 `done rc=0 … --no-gbprime` 줄이 **있으면** (SIGINT 중단) `--no-gbprime` 재개를 **넣지 않는다** — 적합 15 개가 미완이어도, GB′ 줄이 아직 큐에 없어도 기다린다; 적합이 갖춰지는 즉시 감시가 넣는 GB′ 작업이 그 학습을 `# resume` 없이 이어 마친다 (그 구간은 학습 구간이고 GB′ 증거는 `gbp_<T>.log` 다). 적합 15 개 전에 재개를 넣으면 재개가 도는 동안 적합이 갖춰질 때 감시가 GB′ 를 넣어 두 작업이 같은 ckpt 를 쓴다. (2) 그 줄이 **없으면** — `done rc=` 줄 자체가 없음 (세션이 죽어 rc 줄 없이 끝남; 감시는 태그를 들고 있으나 이 줄 없이는 넣지 않는다) 또는 `rc≠0` 로 감시가 태그를 버림 (`gbp_watch.log` 의 `ALERT training rc!=0`) — 그 stem 의 프로세스가 `job_g*` 세션·`nvidia-smi` 에 없음을 확인한 뒤 `--no-gbprime` 재개를 넣는다 (§4.1 의 `--no-gbprime` 명령 문자열 그대로, 감시의 grep 이 그 문자열을 본다); 재개가 rc=0 으로 끝나면 감시가 태그를 들고 있는 경우 그 뒤에 GB′ 를 넣고 (순차), 태그를 버린 경우 주 세션이 GB′ 를 직접 넣는다." 뒤 문장 ("같은 ckpt 를 두 작업이 … §5 에 적는다.") 은 그대로 둔다.
§4.1 GB′ 재실행 행 (:260) 의 괄호 "rc ≠ 0 로 버려진 태그는 재개와 GB′ 를 모두 주 세션이 직접 넣는다" 뒤에 "; `done rc=` 줄이 없는 태그 (세션 사망) 는 주 세션이 재개만 넣고, 그 rc=0 줄이 생기면 감시가 GB′ 를 넣는다; rc=0 줄이 있는 중단은 재개를 넣지 않고 감시의 GB′ 작업이 학습을 이어 마친다 (§1 학습 실패 행)" 를 더한다.
머리말: 5차 bullet 의 stats-fair r5 M2 항목 끝에 "(6차: '없으면 재개' 분기가 적합 15 개 미완 중단에서 감시 GB′ 와 경합 — 재개 여부를 `gpu_sched.log` 의 rc=0 줄로 정하도록 교체, integ6-M1)" 주석, 검토 표에 6차 행과 "6차 적대적 검토 반영" bullet (선례 형식), 제목·상태 v6.

### should
- 줄 번호 인용 정정 (선례 형식은 줄 번호가 정확해야 한다): §1 학습 실패 행 (:133) 과 5차 bullet (:43) 의 `score.py :1030–1031` → `:1031–1032` (실제 `except KeyboardInterrupt:` :1031, `stopped, aborted = "interrupted", True` :1032); :43 과 :45 의 `_already_stopped` `:735–746` → `:737–747` (def :737, `return None` :747); §1 의 `run_d2_sx.py :77–80` 과 5차 bullet 의 `:79–80` 을 `:79–80` 으로 통일 (`if a.no_gbprime:` :79, `sys.exit(0)` :80). `train_nr16.py :68–69` 는 맞다.
- §1 실행 스크립트 행 (:147) 의 전제 문구 "마지막 학습 구간 `# done` (구간 규칙; `# resume` 구간 제외)" 은 '마지막 학습 구간의 `# done`' 으로도 읽힌다. 스크립트 :244 는 '학습 구간들의 마지막 `# done`' 이라 끝난 학습 뒤 `# resume` 전에 죽은 머리말만의 GB′ 시도 (ckpt 무변) 가 있어도 PASS 한다 (r9 가짜 D). §5 체크포인트 행 (:288) 의 "학습 구간 중 마지막 `# done` 줄" 과 같게 "학습 구간 (`# resume` 없는 구간) 들의 마지막 `# done`" 으로 고친다.
- `prep` 은 V1 의 §3d stem (`_fb[23]`) 에 대해 파일 이름만 찍고 (:126 `other attempts of this stem`) ident·`done()` 줄은 attempt 1 stem 만 찍는다 (:121–127). §5 체크포인트 행은 "`prep` 출력 그대로" 를 요구하고 C6 선례는 실제로 fb2 를 썼다 (a1 :1076 diverged). :121–127 을 `for st in [stem] + sorted(os.path.basename(p)[:-3] for p in glob.glob(f'ckpt/{stem}_fb[23].pt')):` 루프로 감싸 (last=f"ckpt/{st}.pt", ident/`done(st)` 를 st 로) fb stem 의 sha256[:16]·epoch·best_epoch·role·best_val·`best.epoch == last.best_epoch`·구간 줄도 함께 출력하게 하면 §5 가 손 계산 없이 채워진다. DRAFT PT 줄은 지금처럼 attempt 1 로 두고 §1 문구 ("손으로 바꾼다") 는 stem·sha 필드에만 남긴다.
- §5 체크포인트 행 (:288) 에 한 절: "감시의 GB′ 작업이 중단된 학습을 이어 마친 경우 (§1 학습 실패 행 (1)) 그 구간은 `# resume` 이 없는 학습 구간이고 GB′ 재실행 구간은 0 개다 — GB′ 증거는 `gbp_<T>.log`·수용 (h) 로만 적는다". 지금 규칙으로는 그 경우 '학습 구간 2·GB′ 구간 0' 으로 전사되는데 §4.1 GB′ 재실행본 행과 모순처럼 보일 수 있다.

### verified
- `bash -n code/run_nscale.sh` 통과. 현재 스크립트와 `nscale_reg/r8/run_nscale_pre_r6.sh` 의 diff = `243a244,245` (TL 두 줄 추가) 뿐 → 라운드 4·6 의 플래그·이름·단일 S5·전제·qk·why·K8·`gl`·`done()` 검증이 그대로 유효. r8 조각 7 개가 현재 스크립트와 바이트 동일 (guard_pre :216–219, guard_write :263, pre_fb :224–225, pre_pt :232–258, qk_fn :451–465, why_fn :414–418, pt/ok :50·:298).
- TL 검사 (:244–245) 를 그대로 추출해 r7 모양 밖의 가짜 로그 9 개로 돌림 (`nscale_reg/r9/`, mawk 1.3.4): PASS — (D) 끝난 학습 + `# resume` 전에 죽은 머리말만의 GB′ 시도, (E) `stopped_by=max_epochs, aborted=False` + GB′ 쌍, (G) 중단 → 감시 GB′ 작업이 한 구간에서 patience 까지 이어 학습 (`# resume` 없음), (J) 중단 → 재개 완주 → 죽은 머리말, (L) 머리말 없는 `# done` (score.py :919 가 항상 머리말을 써 실제로는 없음); ABORT — (F) `max_epochs, aborted=True` (ep < min_epochs), (H) 중단 줄 + 조작된 `# resume` 구간 aborted=False, (I) diverged + 발산 ckpt 의 GB′ 재실행 (`# resume … stopped_by=diverged`), (K) 중단 → 재개가 `# done` 없이 죽음. 하네스의 `die` 는 return 이라 ABORT 뒤의 PASS echo 는 하네스 흔적이다. 드래프터 `r8/t_tl.out` (가짜 8 + 선례 5)·`t_pre2.out` (9 경우) 의 PASS/ABORT 자리도 기대와 일치.
- 선례 로그 grep (BLER 아님): `logs/train_d2sx_NR16_N160000_a1.log` :2 머리말·:1076 `stopped_by=diverged, aborted=False`; `…_a1_fb2.log` :2·:1712 patience; `…_a1_fb3.log` :2 머리말만; `ckpt/` 에 `d2sx_NR16_N160000_a1{,_best,_fb2,_fb2_best,_fb3,_fb3_best}.pt` 존재 → integ5-M1 의 결함 경로 (sha 일치로 발산 ckpt 통과) 가 현재 TL 검사로 막힘을 확인 (t_tl.out 의 a1 ABORT).
- 감시 ↔ 스케줄러 형식: `~/t2_wtS/conf/code/gpu_sched.sh` :20 이 세션 끝에 `done rc=$rc job_g<g>: <cmd>` 를 쓰고, `gbp_watch.sh` :18 의 grep `done rc=0 job_g.: .*<run_d2_sx.py --ntrain N --no-gbprime>` 이 그 줄에 맞는다; :21 `rc=[^0]` 는 rc=0 에 맞지 않고 태그를 버린다; :16 발산 검사는 a1 로그만 본다; 태그는 큐·ALERT 때만 `left` 에서 빠진다 (:17, :20, :21). 감시 글롭 `fit_S2_Nr8_*_n320000.npz` 를 선례 `gmm_fits_D2_B32e4` 에 적용 → 24 파일 중 15 (full 6 + kron 9; `.k0r*` 후보 9 제외), `gmm_fits_D2_NR16B16e4` 도 15 → §4.1 의 '15 개' 서술이 맞다. tmux `nsgbp` 세션이 있고 `logs/nscale/gbp_watch.log` 는 `start` 두 줄뿐 (queued·ALERT 없음) → 세 태그 모두 아직 감시 중 (M1 의 경로가 살아 있음). `gpu_sched.log` 는 열지 않았다.
- 코드 인용 대조: score.py `# =====` :919, `# resume` :957, KeyboardInterrupt :1031–1032, `# done` :1036, `_already_stopped` :737–747 (diverged → patience → max_epochs → None); run_d2_sx.py `if a.no_gbprime: sys.exit(0)` :79–80; train_nr16.py `if a.no_gbprime: return 0` :68–69. 학습 로그·ckpt 이름: run_d2_sx :63–68 `d2sx_N<N>_a<k>[_fb<k>]` ↔ `logs/train_d2sx_<tag>.log`, train_nr16 :54–58 `d2sx_NR16_N<N>_a<k>[_fb<k>]` ↔ 같은 규칙 → :244 의 `logs/train_$3.log` 가 S5 stem (fb 포함) 의 로그를 가리킨다.
- 스크립트가 쓰는 python 플래그는 전부 argparse 에 있다 (eval_accept :46–63, frontier_ci :358–369, recovery_ci :47–51, guard_report :81–82, run_manifest :37–38, runner :1200–1270) — 라운드 4 검증과 같고 호출 줄은 바뀌지 않았다.
- 열지 않은 것: NSCALE 학습 로그·체크포인트 내용·적합 npz·적합 로그, `gpu_sched.log`·`gpuq.txt`, `samplecx.csv` 의 새 행, `~/t2_wtS` 의 어떤 파일, SEEDSNR·`*NR32_N160000_a3_fb3*`. GPU·BLER·커밋·삭제 명령 없음, 시각 입력 없음. 스크래치는 `nscale_reg/r9/` 에 남겼다.

