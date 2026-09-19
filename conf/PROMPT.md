# PROMPT — Claude Code 실행용

> **복사용 단독 평문 파일이 따로 있다.** 이 파일은 사본 + 실행 전 체크리스트다.

## A. 실행 전 체크리스트 (사용자)

1. `conf/` 폴더를 repo 루트에 업로드하고 push.
2. 서버에서 **tmux 안에서** Claude Code를 띄운다. 이번엔 며칠 갈 수 있으므로 필수다.

       tmux new -s conf
       cd ~/t2/T2-Annealed-receiver   # 경로는 본인 것
       claude

   나중에 `tmux attach -t conf`.
3. **모델 = Opus, effort/thinking = Max.** `/model`로 설정한다. 프롬프트 첫 블록이 다시 확인한다.
4. **자동 승인(auto) 모드**를 켠다.
5. 아래 §B를 통째로 붙여넣는다.
6. 원격 확인 경로:
   - **휴대폰 GitHub**에서 `conf/STATUS.md`, `conf/LADDER.md`, `conf/DECISIONS.md`, `conf/BLOCKERS.md`.
   - **Claude 모바일 앱**으로 세션에 원격 접속.

**범위 메모.** 이번 실행은 baseline 2종 + 우리 모델 + **diffusion score 학습(사다리 L1~L6)** + **주장용 testbed D2 구축**까지다. 시간 제한 없음. 사다리의 심판은 BLER이 아니라 사전 등록 게이트(GA~GD)다.

---

## B. 붙여넣을 프롬프트

```
[세션 설정 확인 — 첫 줄에서]
이 작업은 모델 Opus, effort/thinking Max 기준으로 설계돼 있다. 현재 세션이 그렇지 않으면
지금 바로잡고 시작해라(/model 로 Opus 선택, effort 를 Max 로). 확인한 설정을
conf/STATUS.md 맨 위에 적어라.

git pull.

역할: 이 저장소의 conf/ 폴더에 적힌 지침만 보고, conference 논문용 실험을 코드부터 결과까지
끝까지 완성한다. baseline 구현, 우리 모델 조립, diffusion score model 학습, 주장용 testbed
구축, 전 arm 실행까지 전부 포함한다.

[먼저]
conf/README.md 를 읽고, 거기 적힌 순서대로 conf/00_GOAL.md, 01_RULES.md, 02_SPEC_baselines.md,
03_SPEC_ourmodel.md, 04_SPEC_diffusion.md, 05_SPEC_testbed_D2.md, 06_SPEC_runner.md,
07_SPEC_tests.md, 08_SPEC_analysis.md, 09_PRIOR_ART_NOTE.md 를 전부 읽어라. 하나도 건너뛰지
마라. 09번에 BiG-AMP 원문의 부호 오타와 구조적 한계가 적혀 있다.
그 다음 Demo/t2_route_a.py, Demo/t2_trellis.py, Demo/t2_gmm.py, Demo/exp_0925_run.py,
Demo/exp_0925_analysis.py, Demo/exp_0915_bcjr_score_check.py, CLAUDE.md 를 읽고 기존 API·
반환 포맷·시드 규약을 파악해라. 지침의 함수 이름과 repo가 다르면 repo가 정본이다.

[시간]
시간 제한은 없다. 며칠이 걸려도 된다. 대신 conf/00_GOAL.md §3 의 Stage A(A0~A6) →
Stage B(B1~B4) 순서와 각 단계의 종료 조건(게이트)을 건너뛰지 마라. 빨리 끝내려고 검증을
생략하는 것이 이 작업에서 가장 큰 손실이다. n 은 어느 경우에도 640 미만으로 낮추지 마라.

[작업 순서 — 바꾸지 마라]
Stage A (testbed D1, 계측):
  A1 baseline R3·R4 구현 → 테스트 B·S·C 전부 PASS
  A2 우리 모델 조립 → 테스트 M1~M4 PASS (특히 M2)
  A3 F2 lemma 재현 (Demo/exp_0915_bcjr_score_check.py 를 수정 없이) → L1·L2
  A4 sigma_t 격자를 "측정해서" 확정 (04_SPEC_diffusion.md §3). 임의로 고르지 마라
  A5 score 사다리 L1→L6, 각 칸 최대 3회 재시도, 게이트 GA~GD 로 심판
  A6 D1 에서 전 arm 실행 (헤더에 순환 testbed 경고)
Stage B (testbed D2, 주장):
  B1 sparse specular 생성기 구축·검증 → T2a~T2e (특히 T2d)
  B2 GMM 재적합·b* 재선택 (검증 우도만)
  B3 sigma_t 격자 재측정 + score 재학습 (아키텍처는 D1 통과본 고정, 재탐색 금지)
  B4 D2 에서 전 arm 실행 = headline

우리 모델을 baseline 보다 먼저 만들지 마라. M2(Module H 만 Gaussian 으로 되돌리면
R2-ours-G 와 로그 차이 0.0)가 FAIL 이면 우리 모델 arm 전체를 FAILED-VERIFICATION 으로
표시하고 baseline 만으로 진행해라. T2d 가 FAIL 이면 Stage B 를 진행하지 말고 BLOCKERS.md 에
올려라 — 검증 안 된 testbed 의 숫자는 못 쓴다.

[사다리 — 가장 중요한 규칙]
diffusion 은 여러 모델을 시도한다. 실패하면 다음 칸으로 간다. 다만 "실패"의 정의가 전부다.
- 게이트(GA~GD) 미달 → 정당한 실패. 같은 칸 최대 3회 재시도 후 다음 칸.
- BLER 이 나쁨 → 이것은 실패가 아니다. BLER 을 보고 사다리로 되돌아가는 것은 금지다.
  게이트를 통과한 모델의 BLER 결과는 나빠도 그대로 받아들인다.
- 게이트 기준(GA 1e-6, GB +5%, GC 0.15, GD 0.20)을 실행 중에 낮추지 마라.
- 모든 시도를 conf/LADDER.md 에 append 해라. 실패한 시도도 지우지 마라. 이 로그가 남아
  있어야 "결과를 보고 고르지 않았다"를 보일 수 있다.
- 전 칸이 게이트에 도달하지 못하면, 학습 score arm 없이 나머지를 완주하고 "이 데이터
  예산에서 학습 score 는 게이트에 도달하지 못했다"를 결과로 보고해라. 이건 실패가 아니라
  findings 다.
- diffusion 에 GMM 보다 많은 데이터나 예산을 주지 마라. 동일 N_train=1e4, 동일 분할이다.
- D2 에서 아키텍처를 다시 탐색하지 마라. D1 에서 게이트를 통과한 구성을 그대로 쓴다.

[testbed 서술]
D2 를 고른 근거는 "물리적으로 표준인 mmWave 희소 다중경로라서"이지 "GMM 에 불리해서"가
아니다. 후자를 문서·코드 주석·결과 파일 어디에도 쓰지 마라. 조건부 Gaussian 이 깨지는 것은
그 물리의 귀결이고, T2d 가 그 직접 증거다.
D1 결과 표에는 "순환 testbed — 참 prior 가 격자 GMM 으로 정의되어 GMM arm 이 correctly
specified. 학습 prior 에 대한 주장 불가" 경고를 반드시 넣어라. D1 과 D2 표를 합치지 마라.

[운영 모드 — 중요]
나는 오랫동안 접속하지 않는다(며칠일 수 있다). 질문을 남기고 멈추면 그 시간이 통째로 날아간다.
- 모호한 지점은 conf/01_RULES.md §4 fallback 표를 적용하고, 없으면 우리 주장에 불리한 쪽을
  택하고, conf/DECISIONS.md 에 한 줄 남기고 계속 진행해라. 나에게 묻지 마라.
- 멈춰도 되는 경우는 conf/01_RULES.md §3 의 hard stop 3가지와 T2d 실패뿐이다. 그때도
  BLOCKERS.md 를 쓰고 그때까지의 산출물을 전부 push 한 뒤 종료해라.
- 테스트 FAIL, 학습 발산, 수렴 실패는 멈출 이유가 아니다. §6 절차대로 처리하고 계속 가라.
- 계획 수립·알고리즘 구현·디버깅은 직접 깊게 생각해서 하고, 대량 파일 읽기·로그 파싱·결과
  집계·반복적인 정리 작업은 가벼운 모델의 서브에이전트에 위임해라.

[학습은 반드시 실제로 한다 — 형식적으로 넘기지 마라]
- 러너에 train / gate / sigma / testbed 서브커맨드를 만들고, 학습을 실제로 실행해라.
  conf/ckpt/ 에 최소 L1·L2·L3 세 칸의 체크포인트 파일이 실재해야 한다(테스트 D4t 가 확인한다).
- 한 칸을 "시도했다"고 하려면 검증 loss 20 epoch 무개선으로 조기 종료했거나 최소 200 epoch 에
  도달해야 한다. 그 전에 그만둔 것은 LADDER.md 에 ABORTED 로 적고 칸을 소진한 것으로 세지 마라.
  대충 돌리고 "게이트 미달"로 넘어가면 사다리 전체가 무효다.
- LADDER.md 각 행에 학습 epoch 수, 최종 검증 loss, 학습 wall-clock, device 를 적어라.
  학습 로그는 conf/logs/train_*.log 에 device 와 epoch 당 시간이 남아야 한다.
- "학습 arm 없이 진행"은 위 증거가 전부 있고 그럼에도 게이트를 못 넘었을 때만 유효한 결론이다.
  학습을 시도하지 않고 그 경로로 빠져나가지 마라.

[계산 자원]
자세한 규칙은 conf/01_RULES.md §9. 요약:
- 시작할 때 nvidia-smi 로 가용 GPU 와 메모리를 확인하고 STATUS.md 에 적어라.
- score model 학습(A5, B3)은 처음부터 GPU 를 써라(train/gate 의 --device 기본값은 cuda).
  여기서는 GPU 가 명백한 정답이니 측정해 볼 필요 없다. 학습은 float32 로 해도 된다.
  체크포인트는 conf/ckpt/ 에 저장하고 git 에 커밋하지 마라(경로·크기·해시만 STATUS 에).
  중단되면 체크포인트에서 재개해라. 처음부터 다시 돌리지 마라.
- GPU 가 없거나 점유 중이면: 수신기 실행은 CPU 로 진행하되, 학습은 CPU 로라도 반드시 수행해라.
  입력이 64 실수 차원이라 CPU 에서도 된다. STATUS 에 "GPU 없음, CPU 학습" 을 적고 epoch
  예산은 유지해라. 어느 경우에도 학습을 건너뛰지 마라.
- 수신기 실행은 CPU 멀티프로세스가 기본이다(192코어, --jobs 지정하지 마라). GPU 는 측정된
  병목에만, 그리고 전 arm 에 동일하게. 한 arm 만 GPU 로 돌리면 paired 비교가 무효다.
- 추론 정밀도는 전 arm 동일(기본 complex128). GPU 추론을 쓰면 테스트 G1·G2 를 통과해야 하고,
  G1 의 블록별 판정 일치가 깨지면 GPU 경로를 폐기하고 CPU 로 돌아가라.
- OOM 이면 배치를 절반씩 줄이고, 3회 실패하면 CPU 로 폴백하고 DECISIONS 에 기록해라.

[절대 규칙]
- 쓰기는 conf/ 안에서만. 유일한 예외는 종료 시 docs/EXPERIMENTS.md 에 한 행 추가.
- Demo/t2_route_a.py, Demo/t2_trellis.py, Demo/t2_gmm.py, Demo/exp_0915_bcjr_score_check.py 를
  절대 수정하지 마라. 읽고 import 만 해라. 작업 끝에 git status 로 확인해라.
- docs/logs/, docs/plans/ 수정 금지. 기존 Demo/exp_* 결과·raw 삭제·덮어쓰기 금지.
- 우리 모델은 기존 클래스 생성자 기본값에 기대지 말고 전 설정을 명시적으로 넘기고 config 를
  덤프해라. RouteA 기본값은 D-15 설정과 다르다. 조용히 다른 수신기를 돌리게 된다.
- 논문 알고리즘을 기억으로 재구성하지 마라. conf/02_SPEC_baselines.md 에 옮겨 놓은 식만 써라.
  BiG-AMP damping 식 (95)의 부호 오타 경고를 반드시 읽어라.
- 결과가 기대와 달라도 설정을 바꿔 재실행하지 마라. 실패·발산 블록을 표에서 빼지 마라.
  GMM arm 을 약화시키지 마라(D2 에서도 K 전 범위 + shrinkage + 검증 우도 early stopping).
- 다단계 annealed sampling(R-A)은 넣지 마라. 이미 기각됐다. 인터페이스는 one-shot Tweedie +
  D-13 + D-14 로 고정이고, oracle arm 과 학습 arm 이 동일한 인터페이스를 써야 한다.

[보고 — 내가 볼 수 있는 유일한 창]
- 긴 실행은 tee 로 conf/logs/ 에 남겨라. stderr 는 별도 파일로.
- conf/STATUS.md 를 매 단계 종료 시 + 최소 30분마다 갱신하고 그때마다 commit & push 해라.
  마지막에 몰아서 push 하지 마라. 중간 산출물도 같이 push 해라.
- 학습처럼 오래 걸리는 단계에서는 진척(에폭, 검증 loss, 예상 남은 시간)을 STATUS 에 적어라.
- 커밋 메시지 형식: "conf: <단계> <한 줄 요약>"

[완료]
conf/00_GOAL.md §4 의 DoD 9개가 전부 참이면 끝이다. 끝나면 STATUS.md 를 최종 상태로 쓰고,
docs/EXPERIMENTS.md 에 한 행 추가하고, 전부 push 하고, 마지막에 다음을 한 화면으로 요약해라:
  (1) 통과한 테스트와 잔차 — 특히 M1, M2, L1·L2, T2d
  (2) 사다리 결과 — 칸별 GA~GD, 어느 칸이 통과했나, 총 시도 수,
      학습에 쓴 device, 칸별 epoch 수·검증 loss·wall-clock, ckpt 파일 경로와 크기
  (3) D2 testbed 검증 결과 (T2a~T2e)
  (4) 완료한 셀·SNR 점·n (D1 표 / D2 표 따로)
  (5) 표 A/B/C/D 파일 경로
  (6) DECISIONS 목록, BLOCKED 항목
  (7) device / 정밀도 / GPU 를 썼다면 G1·G2 결과
  (8) 내가 판독할 때 먼저 볼 3가지

지금 시작해라.
```

---

## C. 사용자가 돌아와서 할 일 (판독 순서)

1. `conf/STATUS.md` → 어디까지 갔는지, 세션 설정, device.
2. `conf/DECISIONS.md` → 자율 판단이 설계 의도와 어긋난 게 없는지. **여기가 제일 중요하다.**
3. `conf/results/tests.txt` → **M2 → L1·L2 → T2d** 순. M2 FAIL이면 우리 모델 숫자를 읽지 않는다. T2d FAIL이면 D2 표를 읽지 않는다.
4. `conf/LADDER.md` + `conf/results/gate_D1.txt` → 사다리가 정직하게 돌았는지. 시도 수와 로그 행 수가 맞는지.
5. `conf/results/gmm_fit_D2.txt` → GMM arm이 허수아비가 아닌지. D1 대비 얼마나 나빠졌는지.
6. `conf/results/` **D2 표** (headline) → 그 다음 D1 표 (맥락).
7. 웹 세션에 `conf/results/*.txt`와 `LADDER.md`를 올려 판독.
