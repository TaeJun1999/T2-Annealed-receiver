# NEXT_EXPERIMENTS_SEEDSROOM16e4 — Sionna RT 방 두 풀의 시드 강건성: SRB (무작위 위치) · SRP (경로), 시드 a2·a3, 동일예산 N′ = 1.6e5 (사전 등록 v2)

- 작성: 2026-10-12 09:06 CDT, Claude Code (Opus 5.5), 초안 v1 (미커밋; sha256[:16] 9dfba89cd7ec5e0d, 10-12 09:06 CDT) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-11/review_SEEDSROOM16e4.md`: 그대로 실행 가능, MUST 1 · SHOULD 4 · NIT 6 — 전부 반영, §4) → **v2 2026-10-12 09:25 CDT = 동결 커밋 = 실행 커밋**(§5 는 이미 채워져 있다 — 시드 학습이 끝나 있다; `conf/DECISIONS.md` 같은 줄) → CPU BLER. 커밋 뒤 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_SEEDS16e4.md` §1–§3 (라벨·수용·태그 관례 — **그대로** 쓴다) 와 `NEXT_EXPERIMENTS_SEEDS3_16e4.md` (라벨의 절대 범주 표현, 재개 보장 범위 공개); a1 태그의 셀·적합·격자는 `NEXT_EXPERIMENTS_ROOM16e4.md` §1·§5 (SRB) · `NEXT_EXPERIMENTS_PATH16e4.md` §1·§5 (SRP); `08_SPEC_analysis.md` §2.
- **작성 시점 공개**:
  - 사용자 지시(2026-10-12 CDT, 원문): 이 세션이 "시드별 BLER 을 돌릴지" 를 물은 데 대한 답 **"3. 해보자"**, 같은 메시지의 "남은 gpu 다 써", 그리고 준비 중에 온 **"Cpu 너무 과하게 점유하지 마. 192개 중 절반 정도만 점유해"**. 설계 선택(SEEDS3_16e4 의 틀을 그대로, 두 풀을 한 문서로, 7 SNR 전부)은 작성자가 했다.
  - 이 등록은 두 풀의 a1 결과 전부(ROOM16e4 §6 · PATH16e4 §6, 그림 보강 FIGHSROOM16e4 · FIGHSPATH16e4 · FIGHSX16e4)와 앞선 시드 등록(SEEDS16e4: D2 · UMi28; SEEDS3_16e4: D3 · SV8e · MIX3; SEEDSNR16e4: Nr 16/32 세 셀; "시드 강건 3/3" 이 다수)의 결과를 **본 뒤** 쓴다. DMC · SRT 의 a2 · a3 체크포인트는 있으나 평가된 적 없다 — 시드 BLER 을 보고 풀을 고른 것이 아니다.
  - **a2·a3 학습은 이 등록보다 먼저, 등록 없이 끝났다**(학습만; 사용자의 "GPU는 계속 뭐라도 점유하게 돌리고 있어" · "GPU 빈거에 뭐라도 하자" 에 따라 빈 GPU 에 넣음): SRP a2 · a3 — 10-11 14:20 → 16:47 · 19:20 CDT (GPU 0; `logs/seeds_SRP_train.log`), SRB a2 · a3 — 10-11 19:26 → 10-12 00:55 · 01:33 CDT (GPU 0 · 2; `logs/seeds_SRB_train.log`). 네 시드 모두 시행 1 (클리핑 없음), `stopped_by = patience`, 중단·재개 없음(검토가 확인: 학습 로그 `logs/train_d2sx_{SRB,SRP}_N160000_a{2,3}.log` 의 학습 머리말은 하나씩이고 epoch 줄 수 = last 의 epoch (1357 / 1519 / 764 / 783); GB′ 단계가 `run_d2_sx.py` 재개로 학습기를 다시 열어 "no epoch trained … left untouched" 머리말을 하나 더 쓴다 — 체크포인트의 mtime·sha 는 그대로). 학습 스크립트는 세션 스크래치에 있었다(등록 실행 중 `conf/code` 를 건드리지 않으려고; 명령은 §1 의 것 그대로).
  - **이 등록이 평가하는 체크포인트는 어느 수신기로도 평가된 적 없다**: `raw_SR{B,P}B16e4s*` 없음; `logs/run_D2_*.log` 에 `_a2` · `_a3` stem 없음(검토가 확인할 것). 작성자가 본 것은 학습 로그의 epoch · 검증손실뿐이다(판정량 아님; §5).
  - **등록 밖에서 돈 것·도는 것 (동결 시점 기준)**: 시드 a4 · a5 의 학습 네 개(SRB · SRP; GPU 0–3)는 10-12 09:03 CDT 에 시작했다가 **09:15 CDT 에 SIGINT 로 멈췄다**(등록 시드는 a1..a3; 사용자 "추가시드해야하나?" — 필요하지 않다; `logs/seeds_SR{B,P}_train.log` 의 NOTE 줄). 부분 체크포인트 `ckpt/d2sx_SR{B,P}_N160000_a{4,5}*.pt` 는 남아 있고 이 등록은 평가하지 않는다(분모 3 고정; 쓰려면 새 등록). a2 · a3 의 동일예산 GB′ (GPU 4 · 5, 09:03 CDT ~, a2 다음 a3; 보고 전용, BLER 이 아니다 — §1 보고 전용 행): **v1 (sha256[:16] 9dfba89cd7ec5e0d, 09:06 CDT) 의 §1–§3 은 a2 · a3 의 GB′ 값이 하나도 없을 때 썼고, v2 는 §3 예측을 바꾸지 않았다**(검토가 v1 해시를 09:07 CDT 에 읽었다 — `prereg_reviews_2026-10-11/review_SEEDSROOM16e4.md`; v2 의 §1 변경은 그 검토의 M1 · S1 · S2 · S4 · N1 문구뿐, §3 은 8 번의 "(채점 제외)" 꼬리표뿐). **동결 전에 나온 GB′ 값은 §5 추가 줄에 있다**(SRB a2 09:13 CDT · a3 09:21 CDT); SRP a2 · a3 의 값은 동결 시점에 아직 없다(a2 계산 중, GPU 5) — BLER 중·뒤에 나온다.
- 목적: SEEDS16e4 와 같다 — "검증손실로 고른 시드 a1 이 운이 좋았던 것 아닌가". 같은 레시피·예산·GMM b\*·테스트 시행에서 확산 체크포인트만 바꾼다. 두 풀의 a1 판정(둘 다 표 B (i), baseline 16 개 전부 (i))은 어느 결과에서도 바뀌지 않는다; 산출은 **풀별 시드 강건성 라벨 2 개**다.
- **SRP 의 GMM 캐비엇은 그대로 붙는다**: SRP 의 b\* ("kron 4096", ll_val 244.1932863626755, it_best 0) 는 EM 이 무너져 선택된 씨앗 초기화이고 잘 맞춘 GMM 이 아니다(PATH16e4 §5 · 6.1 · 6.7). SRP 의 시드 라벨은 "그 b\* 대비" 의 강건성이다 — 라벨 문자열에 한정어를 붙인다(§1).

---

## 0. 출발점 (판정에 쓰지 않는다; ROOM16e4 §6 · PATH16e4 §6 전사)

| | SRB a1 (`raw_SRBB16e4`, `_best` @1660) | SRP a1 (`raw_SRPB16e4`, `_best` @694) |
|---|---|---|
| 표 B `b* → V1` | −3/0/+3, 209:86 · 65:38 · 28:5, pooled 302:129, POWERED 3/3 → (i) | −3/0/+3, 606:62 · 321:27 · 117:8, pooled 1044:97, POWERED 3/3 → (i) |
| V1 −3 dB BLER@16 (95% Wilson) | 0.275 (0.258, 0.293), 704/2560 | 0.317 (0.299, 0.335), 812/2560 |
| b\* / genie −3 dB | 0.323 / 0.117 | 0.530 / 0.167 |
| SNR@0.1 격차 b\*−V1 (90% paired) | +0.32 [+0.18, +0.45] | +2.01 [+1.78, +2.24] |
| 회수율 R(−3 dB) | 0.233 [0.187, 0.279] | 0.586 [0.554, 0.618] |
| a1 best val | 0.24769899249076843 @1660 | 0.1495504230260849 @694 |

- **이미 정해진 사실**: 판정점은 앵커 b\* 의 BLER 로만 정해지고 §1 수용이 b\* 출력의 a1 비트 동일을 요구하므로, 수용된 시드 태그의 판정점은 a1 과 같다(두 풀 모두 −3/0/+3; 세 점의 b\* BLER 이 [0.005, 0.9] 안 — SV8e 같은 미리 정해진 (iv) 는 없다). SRB 의 0 dB 점은 a1 에서 65:38 (p 0.01) 로 세 점 가운데 가장 약하다.
- 선례: SEEDS16e4 §6 — D2 · UMi28 "시드 강건 (3/3 (i))"; SEEDS3_16e4 §6 — D3 3/3 (i), MIX3 3/3 (i) (보고 전용), SV8e "판정하지 못함"; SEEDSNR16e4 §6 — 세 셀 3/3 (i).

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **체크포인트** | `ckpt/d2sx_{SRB,SRP}_N160000_a{2,3}_best.pt` — 동결 레시피 `run_d2_sx.py --prior {SRB,SRP} --ntrain 160000 --tag {SRBB16e4,SRPB16e4} --attempt 2\|3 --fallback 1 --no-gbprime`, rung D2SX{SRB,SRP}160000 attempt 2/3 (시드 = SEED_TRAIN + rung·17 + attempt; 초기화·배치 순서만 다름), sigma_tag = prior, 분할(split_hash)은 a1 과 같다(§5). **평가 가중치 = `_best.pt`** (a1 판정 태그와 같음); last 는 평가하지 않는다. sha·epoch·best_epoch·stopped_by 는 §5. `stopped_by=diverged` 인 시드는 **"학습 실패(시드 s)"**, 사다리 없음, BLER 없음, 분모 3 고정(SEEDS16e4 와 같은 규칙) — 네 시드 모두 patience 정지라 이 줄은 걸리지 않는다(§5) |
| **바뀌지 않는 것** | GMM b\*·적합: SRB = `gmm_fits_D2_SRBB16e4` (gmm1024 = full K 1024, ll_val 97.00871495382869), SRP = `gmm_fits_D2_SRPB16e4` (kron 4096, ll_val 244.1932863626755); 링크 `results/gmm_fits_D2_<TAG>s{2,3}` → a1 적합 디렉터리(상대 링크, git 미추적 — 선례). 셀 C2, 7 SNR −3..15, n = 2560, 테스트 시행 0..2559 (테스트 풀 복원 추출 — a1 과 같은 시행), chunk 40, 16 반복, 14 arm (a1 raw 의 arm 그대로), CPU complex128, GPU 숨김. **b\*·genie·모든 비-Stage-C arm 의 출력은 a1 태그와 비트 동일**해야 하고 판정점(앵커 b\*)도 a1 과 같다(−3/0/+3) |
| **태그·실행 (명령 원문)** | `tmux new -d -s seedsroom -c /home/HTJ/t2/conf "bash code/run_seedsroom16e4.sh"` (시작 뒤 `logs/run_seedsroom16e4.log` 의 `start` 줄 확인) — 태그 넷을 차례로(SRBB16e4s2 → s3 → SRPB16e4s2 → s3), 태그마다 `taskset -c 24-47,120-143,72-95,168-191 bash code/run_seeds16e4.sh <prior> <TAG> <ckpt> <a1 raw> <bstar> <kron_K> <ll_val> <sha §5> best "<grid>"` 한 번: SRB = `… SRB SRBB16e4s<s> ckpt/d2sx_SRB_N160000_a<s>_best.pt raw_SRBB16e4 gmm1024 2048 97.00871495382869 <sha> best "full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048"` (kron_K 인자 `2048` 은 a1 raw 의 `meta\|kron_K` 값을 채운 자리 값 — b\* 가 full 계열이면 `eval_accept.py` 가 검사하지 않는다; SEEDS3_16e4 의 SV8e 선례), SRP = `… SRP SRPB16e4s<s> ckpt/d2sx_SRP_N160000_a<s>_best.pt raw_SRPB16e4 kron 4096 244.1932863626755 <sha> best "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"`. `run_seeds16e4.sh` 는 SEEDS16e4 의 것 그대로다(수정 없음). 드라이버 `code/run_seedsroom16e4.sh` 가 하는 일: 전제 검사(`conf/code` · `Demo` 청결, 이 문서와 `DECISIONS.md` 추적·청결, 다른 `runner.py run` 없음, 이 등록의 raw 없음), 태그마다 HEAD 불변 검사, 위 호출, `SEEDS_EVAL_DONE` · `ACCEPT: OK -- <TAG>` · `--ref-arms all` 관문(모든 점 shared 2560/2560, 빠진 키 없음, 다른 arm ⊆ {V0, V1, V4, V4b}) 확인 — 셋 다여야 ok (검토 S1; `run_seedsnr16e4.sh` 의 `refok` 와 같은 관문), 끝 줄 `SEEDSROOM_DONE ok=<n> fail=<n>`. 한 태그가 수용되지 않아도 다음 태그는 돈다. **실행 중 규칙**: `SEEDSROOM_DONE` 이 찍힐 때까지 main 에 커밋하지 않고 `conf/code` · `Demo` 에 파일을 만들지 않으며 이 문서와 `DECISIONS.md` 도 건드리지 않는다(HEAD 가 움직이면 드라이버가 다음 태그 앞에서 멈추고, `conf/code` 가 더러우면 `run_seeds16e4.sh` 가 그 태그를 중단한다). 실행 중에 생기는 기록(GB′ 값 등)은 스크래치에 적어 두었다가 끝난 뒤 넣고 커밋한다 |
| **CPU 절반 (사용자 지시; 결과 중립)** | 모든 호출을 `taskset -c 24-47,120-143,72-95,168-191` (NUMA 노드 1 · 3 = 96 스레드 = 물리 코어 48 개 전부) 아래에서 돈다. `runner.py` 에는 설계상 `--jobs` 가 없어(01_RULES §4) 워커는 여전히 192 개가 뜨지만 96 스레드를 나눠 쓴다 — 수신기가 CPU 결정적이고 청크 단위라 **결과는 워커 수·배치와 무관**하다(수용의 a1 비트 동일 검사가 매 태그 확인한다). 달라지는 것은 벽시계 시간뿐이다. 같은 시간대의 등록 밖 GPU 작업(a2 · a3 의 GB′; CPU 쌍 68,164 · 69,165 = 노드 2)은 마스크 밖 스레드에 고정돼 있어 runner 와 코어를 나누지 않는다(a4 · a5 학습은 09:15 CDT 에 멈췄다) |
| **수용 검사** | SEEDS16e4 §1 과 같다(스크립트): `eval_accept.py` (청크 {(40k,40)} × 7, meta ntrain / bstar / kron_K (kron 일 때) / ll_val, ckpt sha·role, iters 16, **R5-genie a1 raw 와 비트 동일**, 격자 완전성) + `--ref-arms all` 의 "arms differing" ⊆ {V0, V1, V4, V4b} (그 밖이면 그 실행 무효 → 원인 기록; 재실행은 사용자 승인). 표 B 의 판정점 = a1 의 것(−3/0/+3) |
| **시드 강건성 라벨** (SEEDS16e4 §1 의 규칙, SEEDS3_16e4 의 절대 범주 표현; 분모 3 = a1·a2·a3) | 풀마다 시드별 표 B `b* → V1` (§2): **(i) = V1 이 적게 실패 (POWERED, ≥ 2/3)**; **(ii)/(iii) = "다름"**; **(iv)/학습 실패/수용 실패 = "판정 못함"**. 집계: 셋 다 (i) → **"시드 강건 (3/3 (i))"**; (ii)/(iii) 가 하나라도 → **"시드 의존 (k/3 (i), m 다름)"**; 그 밖 → **"판정하지 못함 (k/3 (i), j 판정 못함)"**. k·m·j 는 a1 을 포함한 세 시드에서 센다; a1 은 ROOM16e4 §6.1 · PATH16e4 §6.1 의 라벨((i)) 그대로. **SRP 의 한정어(라벨 문자열의 일부)**: SRP 의 집계 라벨에는 `; b* = 씨앗 초기화 GMM` 을 붙인다 — 예: "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)"; 다른 두 집계에도 괄호 안 끝에 같은 꼴로 붙인다 — "시드 의존 (k/3 (i), m 다름; b* = 씨앗 초기화 GMM)" · "판정하지 못함 (k/3 (i), j 판정 못함; b* = 씨앗 초기화 GMM)". 풀·예산·prior 한정 문장이며 arm 주장이 아니다. a1 을 다른 시드로 바꾸지 않고 세 시드를 한 표에 싣는다; BLER 을 본 뒤 시드를 고르지 않는다; 동등성은 주장하지 않는다. 다중성: 태그 4 개의 표 B 는 각각 보고하고 새로 만드는 라벨은 집계 2 개뿐 |
| 보고 전용 | 시드별 −3 dB BLER(b\*, V1, V0, genie; b\*·genie 는 a1 과 같은 값임을 확인), pooled a:b 와 부호검정 p, SNR@0.1 격차와 CI, 회수율 R(−3 dB, 판정점 합)과 CI, V0 가드 발동률, 세 시드의 검증손실·epoch, 시드 간 산포(max − min). **시드별 동일예산 GB′** (a2 · a3; `run_d2_sx.py … --attempt <s> --fallback 1` 의 재개 = 학습 없음 + GB′; GPU; `logs/gbprime_{SRBB16e4,SRPB16e4}_a<s>.log`, `results/d2_gbprime_{SRB,SRP}_N160000_a<s>.npz`) — BLER 이 아니고 어떤 라벨에도 쓰지 않는다; 이 등록의 동결 전에 시작됐고 **일부 값은 동결 전에 나왔다**(§5 추가 줄; §3 예측은 그 전에 썼고 바꾸지 않았다 — 머리말 공개). 나머지는 BLER 중·뒤에 나온다(나오는 대로 스크래치에 적고 §5 추가 줄과 커밋은 `SEEDSROOM_DONE` 뒤). 그림 없음. 계산하지 않음: 𝔅 (pair_baselines), PIL · ALD · SP, last, 그림 보강(n = 20480 / 81920) |
| 비용 [추정; 검토 S4] | CPU: 192 스레드 실측 SRB 28.3 분(best) · 24.8 분(last), SRP 53.2 분(best; 다른 CPU 부하와 겹침) · 41.2 분(last) → 96 스레드(물리 코어 절반)에서 약 2 배: SRB 태그 ≈ 50–57 분, SRP 태그 ≈ 82–106 분, 뒤 단계 ≈ 5 분/태그 → **네 태그 ≈ 4.7–5.8 시간**(시분할 손실 10 % 를 더하면 ≈ 6.3 시간까지) 순차; 첫 청크 줄은 11–25 분 뒤에야 나온다. GPU: 없음(BLER). RAM: a1 실행과 같다(워커 192 개 그대로) |
| 무결성 | 이번 BLER 로 점·arm·가중치·시행을 고르지 않는다. 판정점은 a1 의 앵커 b\*, 가중치는 `_best.pt` (검증손실). 시드 a4 · a5 는 이 등록에 없다 |

## 2. 라벨 (시드마다) — SEEDS16e4 §2 표 그대로
(i) "시드 s 에서 V1 이 b\* 보다 적게 실패" / (ii) "시드 s 에서 b\* 가 V1 보다 적게 실패" / (iii) "판정하지 못함 (유의 방향 없음)" / (iv) "판정하지 못함 (검정력 미달)" — 격자 확장 없음 / 학습 실패 → BLER 없음. 풀·예산·prior 한정; 어느 결과도 a1 판정·기존 등록 §6 을 바꾸지 않는다. SRB 의 캐비엇(ROOM16e4 §2: 유한 풀·한 장소, 이웃, 금속 벽·1 차 반사, 선택 편향)과 SRP 의 캐비엇(PATH16e4 §2 + GMM 씨앗 초기화)이 그대로 붙는다.

## 3. 미리 적는 예측 (a1 과 앞선 시드 결과들을 본 뒤; 각 항목 적중/빗나감)

1. **SRB a2·a3 표 B 모두 (i)** → "시드 강건 (3/3 (i))". (작성자의 확신은 다른 풀보다 낮다 — a1 의 격차가 +0.32 dB 로 작고 0 dB 점이 65:38 이다.)
2. SRB V1 −3 dB BLER: a2·a3 모두 a1 의 95% Wilson CI [0.258, 0.293] 안(닫힌 구간, 3 자리 값).
3. SRB SNR@0.1 격차: a2·a3 의 90% CI 가 a1 의 [+0.18, +0.45] 와 겹친다(교집합 비어 있지 않음; 경계 포함).
4. **SRP a2·a3 표 B 모두 (i)** → "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)".
5. SRP V1 −3 dB BLER: a2·a3 모두 a1 의 [0.299, 0.335] 안.
6. SRP SNR@0.1 격차: a2·a3 의 90% CI 가 a1 의 [+1.78, +2.24] 와 겹친다.
7. 네 태그 모두 수용 통과(`SEEDSROOM_DONE ok=4 fail=0`), `--ref-arms all` 의 "arms differing" ⊆ {V0, V1, V4, V4b}.
8. (채점 제외 — 경로 설명) 빗나갈 경로: 어느 시드가 (ii)/(iii) → "시드 의존", a1 캐비엇, 재선택 없음; 비-Stage-C arm 이 a1 과 다름 → 실행 무효.

## 4. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 |
|---|---|
| a2·a3 학습 4 | **완료**(머리말 '작성 시점 공개'; 네 시드 모두 patience, 발산·재개 없음) |
| fits 링크 4 개 | 생성 10-12 09:05 CDT (링크 mtime; 초안 작성 시각 2026-10-12 09:06 CDT) (`results/gmm_fits_D2_{SRBB16e4,SRPB16e4}s{2,3}` → a1 적합 디렉터리; git 미추적) |
| 드라이버 `code/run_seedsroom16e4.sh` | sha256[:16] 0ce6f000a9d57532 = 검토받은 2608f224c3d0b538 에 검토 S1 의 `--ref-arms all` 관문(검토가 준 코드; 선례 보고서 2 건 통과·변조본과 없는 파일 실패를 다시 확인)과 머리말 두 줄을 넣은 것; 동결 커밋에 포함 |
| 적대적 검토(Fable) → v2 → 동결 = 실행 커밋 → BLER | 검토 끝(10-12 CDT; 그대로 실행 가능, MUST 1 · SHOULD 4 · NIT 6). 반영: **M1** 동결 시점의 공개(추가 시드 중단, 동결 전에 나온 GB′ 값 — 머리말·§1·§5 추가 줄); S1 드라이버의 `--ref-arms all` 관문; S2 실행 중 규칙(§1); S3 §5 머리글(stopped_by 는 last `.pt` 의 값); S4 비용 근거; N1 SRP 한정어의 세 꼴; N2 예측 8 은 채점 제외; N3 앞선 시드 등록의 이름; N4 학습 로그 머리말(사실로 적음); N5 링크 시각; N6 실행 디렉터리(`tmux -c`). 검토가 확인한 것: 드라이버 `bash -n`·인자 10 개 × 4 행, 체크포인트 sha·epoch·분할(§5), fits 링크를 통한 b\* 선택(a1 과 같음), runner 플래그 = a1 호출, `eval_accept` 를 시드 호출 인자로 a1 raw 에 돌려 `ACCEPT: OK` × 4 (full 계열 b\* 에서 kron_K 자리 값 무시), 뒤 단계 도구가 태그가 아니라 prior 로 동작, a1 실행 뒤 수신기 코드 불변, taskset 마스크 = 노드 1 · 3 의 96 스레드, §0 의 모든 수 |

## 5. 평가 전 고정 기록

| 항목 | SRB a2 | SRB a3 | SRP a2 | SRP a3 |
|---|---|---|---|---|
| sha256[:16] · epoch · best_epoch (`_best.pt`) · stopped_by (last `.pt` · 로그 done 줄; 괄호 = last 의 epoch · sha) | **2d3e7eae6bb20008** · 1337 · 1337 · patience (last 1357, sha acb7a0852e306929) | **9f6a9d5042587ae5** · 1499 · 1499 · patience (last 1519, e4d44ff042e936df) | **bdc0f5e854d2abbd** · 744 · 744 · patience (last 764, 19b7aa5915c7d196) | **5db51008da6cc8df** · 763 · 763 · patience (last 783, 0698a00b93de9ca5) |
| 검사: `_best.pt` 의 epoch == last `.pt` 의 best_epoch | 1337 = 1337 ✓ | 1499 = 1499 ✓ | 744 = 744 ✓ | 763 = 763 ✓ |
| best val | 0.24751384556293488 | 0.24783873558044434 | 0.14912495017051697 | 0.14876320958137512 |
| rung · attempt · split_hash (a1 과 같은 분할) | D2SXSRB160000 · 2 · c009329584978bd9 | D2SXSRB160000 · 3 · c009329584978bd9 | D2SXSRP160000 · 2 · 27af93705c6dc289 | D2SXSRP160000 · 3 · 27af93705c6dc289 |
| 참조 raw (a1; `_best` sha) | raw_SRBB16e4 (ed437f21af15c305) | raw_SRBB16e4 | raw_SRPB16e4 (ac4699c78b3e2d80) | raw_SRPB16e4 |

(값은 `torch.load` 와 `sha256sum` 으로 읽었다 — 초안 작성 때; 검토가 다시 확인 — 2026-10-12 09:06 CDT.)

**추가 줄 — 동결 전에 나온 GB′ (보고 전용; 라벨·예측에 쓰지 않는다; `results/d2_gbprime_SRB.csv` · `logs/gbprime_SRBB16e4_a<s>.log` · `logs/seeds_SRB_train.log` 원문; last `.pt`, n_eval 4096, b\* gmm1024)**: SRB a2 — diff/gmm median **0.6158** (min 0.5673 · max 1.0104), 10-12 09:13 CDT; SRB a3 — median **0.6174** (min 0.5698 · max 0.9967), 09:21 CDT; 나란히 a1 0.6472 (min 0.5949 · max 5.1046; ROOM16e4 §6.9). SRP a2 · a3 — 동결 시점에 아직 없음(`results/d2_gbprime_SRP_N160000_a{2,3}.npz` 없음; a2 계산 중).

**추가 줄 — 실행 중에 나온 GB′ (2026-10-12 13:18 CDT 기록; 보고 전용, `logs/seeds_SRP_train.log` 원문; b\* kron 4096)**: SRP a2 — median **0.5860** (min 0.5008 · max 0.9740), 10-12 10:19 CDT; SRP a3 — median **0.5840** (min 0.4943 · max 0.9938), 11:39 CDT; 나란히 a1 0.5836 (min 0.4954 · max 0.9130; PATH16e4 §6.9). 실행 중에는 이 문서를 건드리지 않았고(§1 실행 중 규칙) `SEEDSROOM_DONE` 뒤에 적었다.

## 6. 결과 (이 절은 추가만 한다)

(기록 2026-10-12 13:18 CDT, Opus 5.5)

### 6.1 결과 (생성기 `prereg_audit_2026-10-11/s6_seedsroom_gen.py`; 수치는 모두 기록 파일에서 읽음 — 전사만, 해석 없음)

**실행·수용** — 드라이버 로그 `logs/run_seedsroom16e4.log` 의 시작 · 태그 종료 · 끝 줄(원문):

- `[seedsroom 10-12 09:26 CDT] start (git 62c24e7e) tags: SRBB16e4s2 SRBB16e4s3 SRPB16e4s2 SRPB16e4s3 cpus 24-47,120-143,72-95,168-191`
- `[seedsroom 10-12 10:14 CDT] SRBB16e4s2 done: ACCEPT: OK -- SRBB16e4s2; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 11:04 CDT] SRBB16e4s3 done: ACCEPT: OK -- SRBB16e4s3; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 12:07 CDT] SRPB16e4s2 done: ACCEPT: OK -- SRPB16e4s2; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 13:16 CDT] SRPB16e4s3 done: ACCEPT: OK -- SRPB16e4s3; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 13:16 CDT] SEEDSROOM_DONE ok=4 fail=0`

| 태그 | runner | 수용 | `--ref-arms all` (점 7 개의 '다른 arm' 집합) | manifest git · config_hash |
|---|---|---|---|---|
| SRBB16e4s2 | 44.0 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRBB16e4s2` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |
| SRBB16e4s3 | 45.6 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRBB16e4s3` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |
| SRPB16e4s2 | 58.9 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRPB16e4s2` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |
| SRPB16e4s3 | 64.0 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRPB16e4s3` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |

| 태그 | 표 B `b* → V1` 판정점 a:b (p) · pooled (p) | 가드 · 방향 | 라벨 | SNR@0.1 격차 b\*−V1 [90 %] | V1 −3 dB BLER (95 % Wilson) | b\* · genie −3 dB 실패 수 | R (−3 dB) [90 %] | R (판정점 합) [90 %] |
|---|---|---|---|---|---|---|---|---|
| SRB a1 (SRBB16e4; §0 인용) | 209:86 (5.6e-13) · 65:38 (0.01) · 28:5 (6.6e-05) · 302:129 (4.5e-17) | POWERED (3/3), V1 3/3 · b\* 0/3 | (i) | +0.32 [+0.18, +0.45] | 0.275 (0.258, 0.293), 704/2560 | 827 · 299 | 0.233 [0.187, 0.279] | 0.256 [0.212, 0.299] |
| SRB a2 (SRBB16e4s2) | 211:95 (2.9e-11) · 62:30 (0.0011) · 26:5 (0.00019) · 299:130 (2e-16) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +0.35 [+0.22, +0.48] | 0.278 (0.261, 0.295), 711/2560 | 827 · 299 | 0.220 [0.174, 0.268] | 0.250 [0.208, 0.293] |
| SRB a3 (SRBB16e4s3) | 207:106 (1.2e-08) · 66:30 (0.00031) · 24:9 (0.014) · 297:145 (4e-13) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +0.37 [+0.24, +0.51] | 0.284 (0.266, 0.301), 726/2560 | 827 · 299 | 0.191 [0.141, 0.241] | 0.225 [0.178, 0.270] |
| SRP a1 (SRPB16e4; §0 인용) | 606:62 (4.3e-113) · 321:27 (5.2e-65) · 117:8 (5.9e-26) · 1044:97 (4.1e-201) | POWERED (3/3), V1 3/3 · b\* 0/3 | (i) | +2.01 [+1.78, +2.24] | 0.317 (0.299, 0.335), 812/2560 | 1356 · 428 | 0.586 [0.554, 0.618] | 0.644 [0.620, 0.667] |
| SRP a2 (SRPB16e4s2) | 591:64 (8.5e-108) · 307:18 (4.9e-69) · 112:6 (2.1e-26) · 1010:88 (3.6e-199) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +1.95 [+1.73, +2.18] | 0.324 (0.306, 0.342), 829/2560 | 1356 · 428 | 0.568 [0.536, 0.597] | 0.627 [0.603, 0.649] |
| SRP a3 (SRPB16e4s3) | 603:67 (9.2e-109) · 325:18 (5.1e-74) · 115:8 (2.1e-25) · 1043:93 (6e-204) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +2.12 [+1.90, +2.35] | 0.320 (0.303, 0.339), 820/2560 | 1356 · 428 | 0.578 [0.544, 0.607] | 0.646 [0.622, 0.668] |

**시드 강건성 라벨 (§1; 분모 3 = a1·a2·a3)**:
- **SRB: "시드 강건 (3/3 (i))"** (시드별 라벨 a1 (i) · a2 (i) · a3 (i)).
- **SRP: "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)"** (시드별 라벨 a1 (i) · a2 (i) · a3 (i)).

**보고 전용**:
- SRB 시드 간 산포 (a1 / a2 / a3; max − min): SNR@0.1 격차 +0.32 / +0.35 / +0.37 dB (0.05); V1 −3 dB 실패 수 704 / 711 / 726 (22); R(−3 dB) 0.233 / 0.220 / 0.191 (0.042).
  - 동일예산 GB′ SRB a2 (10-12 09:13 CDT, rc 0; b\* gmm1024 (full K=1024)): median 0.6158 (min 0.5673 · max 1.0104).
  - 동일예산 GB′ SRB a3 (10-12 09:21 CDT, rc 0; b\* gmm1024 (full K=1024)): median 0.6174 (min 0.5698 · max 0.9967).
  - V0 가드 (SRBB16e4s2; `results/guard_D2_SRBB16e4s2.txt`): `C2       -3 M-ours-dscore-C-V0          2560   2560   1.000  8.632e+08`
  - V0 가드 (SRBB16e4s3; `results/guard_D2_SRBB16e4s3.txt`): `C2       -3 M-ours-dscore-C-V0          2559   2560   1.000  3.461e+10`
- SRP 시드 간 산포 (a1 / a2 / a3; max − min): SNR@0.1 격차 +2.01 / +1.95 / +2.12 dB (0.17); V1 −3 dB 실패 수 812 / 829 / 820 (17); R(−3 dB) 0.586 / 0.568 / 0.578 (0.018).
  - 동일예산 GB′ SRP a2 (10-12 10:19 CDT, rc 0; b\* kron (kron K=4096)): median 0.5860 (min 0.5008 · max 0.9740).
  - 동일예산 GB′ SRP a3 (10-12 11:39 CDT, rc 0; b\* kron (kron K=4096)): median 0.5840 (min 0.4943 · max 0.9938).
  - V0 가드 (SRPB16e4s2; `results/guard_D2_SRPB16e4s2.txt`): `C2       -3 M-ours-dscore-C-V0          2560   2560   1.000  7.113e+10`
  - V0 가드 (SRPB16e4s3; `results/guard_D2_SRPB16e4s3.txt`): `C2       -3 M-ours-dscore-C-V0          2560   2560   1.000  1.273e+11`

**§3 예측 채점**:
1. SRB a2·a3 표 B 모두 (i) → **적중** ((i) · (i); 집계 "시드 강건 (3/3 (i))").
2. SRB V1 −3 dB BLER 이 a1 의 95 % Wilson CI [0.258, 0.293] 안 → **적중** (0.278 · 0.284).
3. SRB SNR@0.1 격차의 90 % CI 가 a1 의 [+0.18, +0.45] 와 겹침 → **적중** ([+0.22, +0.48] · [+0.24, +0.51]).
4. SRP a2·a3 표 B 모두 (i) → **적중** ((i) · (i); 집계 "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)").
5. SRP V1 −3 dB BLER 이 a1 의 95 % Wilson CI [0.299, 0.335] 안 → **적중** (0.324 · 0.320).
6. SRP SNR@0.1 격차의 90 % CI 가 a1 의 [+1.78, +2.24] 와 겹침 → **적중** ([+1.73, +2.18] · [+1.90, +2.35]).
7. 네 태그 모두 수용 통과(`SEEDSROOM_DONE ok=4 fail=0`), 다른 arm ⊆ {V0, V1, V4, V4b} → **적중** (`SEEDSROOM_DONE ok=4 fail=0`).
8. (채점 제외 — 경로 설명.)

### 6.2 그림과 공개 사항

- **그림 (보고 전용)**: `conference/figures/F34seed_wide.{pdf,png}` + 기록 `records/paper_f34seed.txt` (`paper_f34seed.py`): (a) SRB, (b) SRP — Proposed 의 시드 1 · 2 · 3, GMM prior, Perfect CSI; 전 SNR n = 2560 (이 등록의 raw 와 a1 raw 그대로; +6 dB 이상은 실패 수가 한 자리라 곡선이 끊기거나 흔들린다 — 판정점은 −3 / 0 / +3 dB). 스크립트가 세 raw 의 GMM · Perfect CSI 실패 수가 같음과 −3 / 0 / +3 dB 의 수 = `recovery_<TAG>.txt` 를 assert 한다.
- **CPU 절반**: runner 는 네 태그 모두 `taskset` 마스크(노드 1 · 3, 96 스레드) 아래에서 돌았다(시작 직후 `taskset -cp` 로 확인: 24-47,72-95,120-143,168-191). runner 시간 44.0 · 45.6 · 58.9 · 64.0 분(§1 추정 SRB 50–57 · SRP 82–106 분); 전체 10-12 09:26 → 13:16 CDT (3 시간 50 분; 추정 4.7–5.8 시간).
- **실행 중 main 커밋 없음**(HEAD 62c24e7e 그대로). 그 사이에 한 것(HEAD·`conf/code`·`Demo`·이 문서·`DECISIONS.md` 는 건드리지 않음): `git push origin main` 과 paper 브랜치 동기화 세 번(원격만 갱신), 작업 트리의 `docs/RESULTS.md` §25 (레이 트레이싱 풀 요약; 미커밋으로 paper 브랜치에 실림), 이 절의 생성기와 그림 스크립트 작성.
- **실행 중에 본 것**: 작성자는 SRB 두 태그가 수용된 뒤·SRP 태그가 도는 동안(10-12 11:17 CDT ~) SRB 의 `tables_D2_SRBB16e4s{2,3}.txt` · `recovery_*.txt` 를 읽어 생성기를 시험했고 SRB 의 결과(3/3 (i))를 사용자에게 보고했다. SRP 의 결과 파일은 `SEEDSROOM_DONE` 뒤에 읽었다. GB′ 값은 §5 추가 줄 둘(동결 전 SRB, 실행 중 SRP).
- 함께 돈 것(결과 중립 — 수신기는 CPU 결정적; 세션 기록 기준): SRP a2 · a3 의 GB′ (GPU 5, CPU 쌍 69,165 — 마스크 밖; 11:39 CDT 까지).
- 등록 밖 체크포인트 a4 · a5 (09:15 CDT 에 멈춘 부분 학습)는 평가하지 않았다.
- 기록 감사(Fable)는 이 절을 쓴 뒤에 받는다 — 결과는 추가 줄로 적는다.
