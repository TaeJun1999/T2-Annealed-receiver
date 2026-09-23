# NEXT_EXPERIMENTS_A1C5 — A1 후속: C5(Tp=3) 를 판정점으로 하는 위상 augmentation 재검정의 사전 등록 (v2)

- 작성: 2026-09-23 11:20 CDT 초안(v1) → 적대적 검토 2건(통계·누출 8건, 규칙·실행 13건; 워크플로 wf_602c3cb5-daa) 반영 v2, 2026-09-23 11:30 CDT 동결 커밋 ad32f48b (= 09-24 01:30 KST; 이 줄에 처음 11:55 CDT 로 적은 것은 잘못 — 2026-09-23 18:03 CDT 정정), Claude Code (Fable 5.1). **결과 관측 전** (a2·a3 체크포인트는 학습 중이고 어떤 체크포인트도 4480 이후 시행에서 평가된 적이 없다). 사용자 결정(2026-09-23 09:40 CDT): "추가 학습 포함 등록". 커밋 뒤에는 §1~§3 의 규칙·임계값·예측을 바꾸지 않는다. 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 근거: `NEXT_EXPERIMENTS.md` v3 §3.1 A1 의 3단계 결과(`A1s3_aug_vs_ctrl_{C2_m3,C2_p6,C5_m3}.txt`), 2단계 결과(`A1s2_group_C2_m3.txt`), H0 (`H0_best_vs_last_C2_m3.txt`). v3 §0 의 고정 사항(테스트 집합 0..2559, house test, 평가 가중치 = `_best.pt`, 결과 보존, CPU 수신기)은 그대로 적용된다.
- 목적: A1 3단계에서 **보고 전용 점 C5 −3 dB 에만** 나타난 신호(aug 238 vs ctrl 260)를 (i) 새 시행에서, (ii) 그 신호를 만든 체크포인트 쌍과 **다른** 학습(attempt 2·3; 초기값·데이터 스트림이 다름)에서 다시 묻는다. 답은 "위상 augmentation 이 Tp=3 < Nt 셀에서 V1 의 실패를 줄이는가" 이지, C2 헤드라인의 교체가 아니다.
- v3 §3.1 과의 관계: v3 의 4단계(테스트 확증)·5단계(헤드라인 교체)는 3단계 판정점 C2 −3 dB 가 판정 불가여서 **발동하지 않았고 그대로 닫혀 있다.** 이 문서의 확증은 그 규칙의 변경이 아니라 사용자 결정에 따른 **별도 추가 등록**이며, 통과해도 v3 5단계를 되살리지 않는다.

---

## 0. 출발점 (이 수치들은 판정에 쓰지 않는다)

| 단계 | 비교 | 결과 |
|---|---|---|
| 2단계 (N=1e4, attempt 1·2·3, 개발 집합 C2 −3 dB, n=640) | 3쌍 평균 부호검정 | aug 85/82/83 vs ctrl 85/85/88, 15:19, p=0.61 → 판정 불가 |
| 3단계 (N=1.6e5, attempt 1 한 쌍, 개발 집합) | 판정점 C2 −3 dB | 84 vs 85, 9:10, p=1 → 판정 불가 → v3 4단계 없음 |
| 〃 | 보고 전용 C2 +6 dB | 4 vs 4, 0:0 |
| 〃 | **보고 전용 C5 −3 dB** | **238 vs 260, a:b = 16:38 (n_d 54), net(a−b) = −22, p=0.0038, MDD 16** (a = aug 만 실패) |

- 이 신호는 보고 전용 2점 중 하나에서 나왔다(사후 선택). 그래서 같은 시행으로는 확인할 수 없고 **새 시행**에서만 확인한다.
- 3단계는 aug 1개·ctrl 1개 체크포인트의 비교이고 초기 가중치는 고정되지 않았다(`CHANGELOG_REVIEW.md` N1, 사용자 결정 "기록만"). 검정의 n 은 시행이고 체크포인트는 고정 조건이므로, 새 시행에 **같은 a1 쌍**을 돌려서는 "a1 aug 체크포인트가 초기값 운으로 C5 에 유리하다" 는 대안 설명을 배제할 수 없다(체크포인트의 성질은 새 시행에서도 그대로 재현된다). 그래서 **1차 검정은 새로 학습한 쌍(a2·a3)만으로** 정의하고, a1 쌍은 보고 전용으로 내린다(§1).
- 같은 시행의 다른 arm(3단계, C5 −3 dB, n=640): GMM b\* 314, genie 25. P3 판정 집합의 C5 −3 dB(시행 3200..3839, 레거시 V1 `d2sx_N160000_a1.pt`): V1 230, b\* 298, genie 30 — aug/ctrl 체크포인트는 그 시행에서 평가된 적이 없다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **판정 집합 (신규)** | C5 −3 dB, 같은 시행 스트림(`common.trial_rng(D2, S2, 8, 16, 3, −3)`)의 **skip 4480 ~ 5759 (n=1280, 청크 40 × 32)**. C5 −3 dB 의 기존 사용: 0..2559 테스트, 2560..3199 개발(A1s3·H0·A2), 3200..3839 P3 보고 전용(레거시 V1·b\* 만) → 4480 부터는 어느 실행에도 쓰인 적이 없다(3840..4479 는 비워 둔다: C2 −3 dB 의 P3 판정 집합 끝(4479)과 시작을 맞춘다) |
| 보고 전용 2점 | **C5 0 dB**(효과가 SNR 위로 이어지는지)와 **C2 −3 dB**(헤드라인 셀에서는 여전히 판정 불가인지의 맥락), 각각 skip 4480..5119 (n=640, 청크 16 × 40). C5 0 dB 는 2560 이후 미사용, C2 −3 dB 는 4480 이후 미사용. 판정으로 승격하지 않는다 |
| **수용 검사 (점별로 고정)** | 6개 태그 모두: (C5, −3 dB) 는 raw 청크 집합이 **정확히** {(4480+40k, 40) : k=0..31}, (C5, 0 dB)·(C2, −3 dB) 는 **정확히** {(4480+40k, 40) : k=0..15}; 그 밖의 조합(부분 실행 포함)은 **거부**. 6 태그의 (skip, n) 목록·run 파라미터(seed, iters 16, beta 0.7, t_in, dtype) 동일; 태그마다 Stage C 체크포인트 id 는 하나이고 `role=best` 이며 `epoch == best_epoch`; 6개 sha256[:16] 은 평가 전에 `DECISIONS.md` 에 적은 값과 일치해야 한다. **b\*·genie 비트 동일**: `M-ours-bstar`·`R5-genie` 의 모든 `KEYS_RAW` 배열이 세 점 모두에서 6 태그 간 비트 동일(기준 = `aug_a1` 태그; 체크포인트와 무관한 arm 이라 같은 시행을 봤다는 증거). 어긋나면 그 실행은 무효 |
| 수용 실패 시 절차 (미리 고정) | 청크 결손·부분 실행 → 같은 태그로 결손 청크만 재실행(runner 는 완료 청크를 건너뜀; 수신기는 결정적) 후 재검사, 최대 1회. b\*·genie 가 태그 간 다르면(코드·fit 링크 오류를 뜻함) 원인을 `DECISIONS.md` 에 적고 **6 태그 전부를 새 태그로 재실행**, 이전 태그는 보존·미사용. 재검사도 실패하면 "수용 실패, 판정하지 않음" |
| 비교 대상 (6 체크포인트, 전부 `/home/HTJ/t2/conf/ckpt_review_next/`) | **aug**: `aug_N160000_a1_best.pt`(3단계의 aug, epoch 1082, sha256[:16] 40c55cb294340594), `aug_N160000_a2_best.pt`, `aug_N160000_a3_best.pt`. **ctrl**: `ctrl_N160000_a1_best.pt`(H0 재학습 = 3단계의 통제군, epoch 1247, sha e2b22673ac91ed8f), `ctrl_N160000_a2_best.pt`, `ctrl_N160000_a3_best.pt`. 역할은 모두 `_best.pt`(3단계와 동일). a2·a3 의 sha·epoch·`stopped_by` 는 학습 종료 후 **평가 전에** `DECISIONS.md` 에 적는다 |
| **쌍의 자격** | attempt k 의 쌍(aug_k, ctrl_k)은 두 학습이 모두 다음을 만족할 때만 자격이 있다: last 파일의 `stopped_by ∈ {patience, max_epochs}`, `aborted = False`, 발산(`diverged`) 아님, `_best.pt` 존재, `ckpt_identity(best).epoch == ckpt_identity(last).best_epoch`. **발산·중단한 attempt 는 `_best.pt` 가 남아 있어도 자격 없음**(score.train 은 발산해도 best 를 지우지 않고 exit 0 이다 — `CHANGELOG_REVIEW.md` §5). 자격 없는 attempt 는 그대로 기록하고 그 쌍은 결측이다 |
| 학습 (a2·a3) | `conf/code/run_a1c5_train.sh` (tmux `a1c5`, GPU 0..3), 2026-09-23 **09:38 CDT** 시작(로그 `run_a1c5_train.log`; 학습 프로세스 헤더 23:39 KST = 09:39 CDT), 코드 f5856204, `train_ctrl.py --ntrain 160000 --attempt {2,3} [--phase-aug]` = attempt 1 과 같은 레시피(레거시 형제 `ckpt/d2sx_N160000_a{2,3}.pt` 와 rung/prior/testbed/Nr/Nt/hp 일치 확인). attempt k 는 데이터 순서·σ·ε 스트림(`SEED_TRAIN + rung·17 + k`)을 바꾸고 학습 채널 집합(N=1.6e5)은 같다; aug 는 위상 generator 를 따로 갖는다; 초기 가중치는 비고정(로그에 `torch.initial_seed` 와 init sha 기록). **학습은 이 문서보다 먼저 시작했지만 어떤 체크포인트도 이 문서가 커밋되기 전에는 평가하지 않는다**(선례: `DECISIONS.md` 2026-09-23 08:40 KST "학습만 미리"). 비교는 3단계와 같이 "초기값 차이 포함" 이다 |
| 자격 (레시피) | aug 레시피의 D1 형제 게이트 PASS(1단계, `gate_aug_D1_N160000_a1.txt`)는 레시피 단위 자격이다. attempt 2·3 은 D2 학습이라 D1 게이트를 측정할 수 없다(D1 형제 없음). GB′·ε_φ 는 보고 전용(아래) |
| 실행 (전부 새 태그) | 체크포인트마다 1회(`conf/code/run_a1c5.sh`, 학습 종료·자격 확인·identity 기록 뒤): `cd /home/HTJ/t2/conf && runner.py run --testbed D2 --cell C5 --snr -3 --prior S2 --skip0 4480 --n 1280 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt_review_next/<ckpt> --arm M-ours-dscore-C-V1 M-ours-bstar R5-genie --tag review_next_A1C5_<aug\|ctrl>_a<k>`; 보고 전용 2점은 같은 태그에 `--cell C5 --snr 0` / `--cell C2 --snr -3` 와 `--n 640`; `ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_<tag>`. 수신기 CPU complex128, 16 반복, `arms.LOOP` 그대로(P3 의 R-adapt 는 쓰지 않는다 — 이 문서는 prior 의 비교다) |
| 실패 지표 | `blk_err[:, −1]` (BLER@16); 예외로 실패한 블록 = 1 (`analysis.load_raw`) |
| **1차 검정 H9 (새 쌍만)** | 시행 i 마다 d_i = ½[fail_aug,2(i) + fail_aug,3(i)] − ½[fail_ctrl,2(i) + fail_ctrl,3(i)]. d_i = 0 인 시행은 버리고, a = #d>0 (aug 가 나쁨), b = #d<0 (aug 가 좋음) 의 **exact 양측 부호검정**(`pair_tags.py group --aug a2 a3 --ctrl a2 a3`; 2단계와 같은 정의, n 은 시행 1280 이고 attempt 를 합쳐 n 을 부풀리지 않는다). 결과는 넷 중 하나: **지지**(p < 0.05 이고 b > a) / **판정 불가**(p ≥ 0.05, n_d ≥ 6) / **UNDECIDED**(n_d < 6) / **반대 방향 유의**(p < 0.05 이고 a > b → 지지 아님, 반대 방향의 유의성은 보고). MDD 는 보고(쌍당 n_d ≈ 108, 2쌍 group n_d ≈ 150~220 → MDD 26~32). 검정 수 **1개**, α = 0.05. **H9 는 a2·a3 두 쌍이 모두 자격이 있을 때만 판정**한다; 한 쌍이라도 결측이면 "판정 불가(쌍 부족)" 이고, 대체 attempt(4) 학습은 사용자 승인이 있을 때만(승인·학습·자격 확인이 모두 **평가 전**이어야 한다) |
| 부차 (보고, 판정 아님) | (1) a1 쌍의 새 시행 paired 부호검정 = 개발 신호(16:38)의 **재현**(체크포인트의 성질). (2) attempt 2·3 각각의 paired 부호검정과 "새 2쌍 중 aug 가 적은 쌍 수 / p < 0.05 인 쌍 수". (3) 3쌍 평균 group 검정(2단계 정의; 판정 아님). (4) 보고 전용 2점에도 같은 세 가지를 찍는다. (5) b\*·genie 실패 수(맥락). 모두 `pair_tags.py` 출력 그대로 |
| 보고 전용 지표 (GPU, 체크포인트마다; 판정에 쓰지 않음) | **GB′**: `runner.py gate --testbed D2` 는 GMM 참조를 N_train=1e4 로 읽으므로 쓰지 않는다. 대신 작은 스크립트(`conf/code/a1c5_report.py`)가 `A.D2_FITS = gmm_fits_D2_B16e4k`, `module_h_priors('D2','S2',8,4, ntrain=160000)` 로 b\* = kron K=1024 를 assert 한 뒤 `score.gb_prime(ckpt, hp['kron'], 'D2', 8, 4, prior='S2', device='cuda')` 를 `results/review_next/gbprime_<tag>.txt` 에 쓴다. **ε_φ**: `diag_p1_heldout.py --ckpt /home/HTJ/t2/conf/ckpt_review_next/<ckpt> --out results/review_next/p1_heldout_<tag> --device cuda` (`--overwrite` 금지 — P1 기록 보존), `phase|` 블록의 위상 비를 읽는다(비등록 ckpt 라 "NOT A VERDICT" 로 찍힘). 실행이 실패하면 그 사실을 적고 판정은 진행한다 |
| 헤드라인 | **바꾸지 않는다.** 헤드라인 V1 체크포인트는 `d2sx_N160000_a1.pt` 그대로. 이 문서가 만들 수 있는 것은 "Tp=3 셀의 별도 행" 뿐이다 |

## 2. 판정·다음 단계 (여기서 고정)

| H9 (새 2쌍) 결과 | 그 다음 |
|---|---|
| 지지 | **테스트 집합 확증 후보** (실행 여부만 사용자 결정, 내용은 아래) |
| 판정 불가 / UNDECIDED / 반대 방향 유의 / 쌍 부족 | A1 은 "개발 집합 보고 전용 신호, 새 학습 쌍의 새 시행에서 재현되지 않음(또는 판정 불가)" 으로 닫는다. a1 쌍의 재현 결과는 보고로만 남는다. 이 문서 아래에서 추가 실행 없음 |

- **테스트 집합 확증(한 번; 실행 여부 사용자 결정)**: 자격 있는 6(또는 a2·a3 만 쓸 경우 4) 체크포인트 각각 새 태그로 테스트 집합 0..2559 의 **C5 −3/0/+3 dB**: `runner.py run --testbed D2 --cell C5 --snr -3 0 3 --prior S2 --skip0 0 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt_review_next/<ckpt> --arm M-ours-dscore-C-V1 R5-genie --tag review_next_A1C5test_<aug\|ctrl>_a<k>` (비용 제한). 점마다 H9 와 같은 **새 2쌍 평균** 부호검정. **통과 = 3점 중 2점 이상에서 aug 가 적고 p < 0.05, 그리고 08_SPEC §2 power guard(3점 모두 있고 ≥ 2점에서 n_d ≥ 6)** — C5 의 테스트 실패율(V1 −3/0/+3 dB ≈ 0.40/0.19/0.12, n=2560)에서는 guard 가 구속력이 없다(형식상 적용). pooled p, 3쌍 평균·쌍별 결과, 나머지 C5 SNR 은 보고 전용. 태그 간 genie 는 점마다 비트 동일. 판정은 `pair_tags.py rule3`(멤버 목록·`--decision C5 -3 0 3` 확장, §5)의 출력으로만 한다. 통과·실패 어느 쪽이든 별도 표로 기록한다.
- 통과했을 때의 문장 범위: "**이** aug/ctrl 체크포인트 쌍들(N=1.6e5, attempt 2·3, 초기값 비고정)에서, 시행에 대한 부호검정으로, C5(Tp=3 < Nt) 의 통과한 SNR 에 한해 aug 의 평균 실패가 적었다". augmentation **자체**의 효과(일반화)는 attempt 수준의 표본(2쌍)으로는 주장하지 않는다. **C2 헤드라인 교체 없음.** 실패하면 "C5 판정 집합에서만 지지" 로 기록한다.
- 이 문서는 2단계·3단계의 결과를 바꾸지 않는다(그 판정들은 그대로 남는다).

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 부호는 `pair_tags` 관행 net(a−b), 음수 = aug 가 적음)

- H9 (a2·a3 group, n=1280): **지지**, net(a−b) = −30 ~ −90 (a1 쌍의 개발 신호 −22/640 → 1280 시행에서 ≈ −44 를 두 새 쌍이 비슷하게 재현하면 group 순은 그보다 커진다; 하한 −30 은 MDD 26~32 근처다). 대안 시나리오를 미리 적는다: a1 의 신호가 초기값 운이었다면 group net ≈ 0, 판정 불가.
- 부차: a1 쌍 재현 net −20 ~ −60, p < 0.05; 새 2쌍 각각 aug 가 적음(2/2), p < 0.05 인 쌍 1~2; 3쌍 group 은 지지.
- 보고 전용: C5 0 dB 는 aug 가 적지만 판정 불가에 가까움(실패 수가 작아 n_d 부족 가능); C2 −3 dB 는 판정 불가(3단계와 같음).
- GB′: aug ≈ ctrl (worst excess 차이 1%p 이내). ε_φ: aug < ctrl (augmentation 이 위상 등변성을 높임).

## 4. 비용

- CPU: 6 태그 × (1280 + 640 + 640) 시행 × (16 반복 블록당 V1 ≈ 1.0 s + b\* ≈ 0.75 s + genie) ≈ 8 CPU-h → 192 워커로 약 5~10 분. 테스트 확증(선택): 6 × 3 × 2560 × ≈ 1.1 s ≈ 14 CPU-h → 약 10 분.
- GPU: GB′·ε_φ 체크포인트당 수 분(GPU 4·5 비어 있음). 학습(a2·a3)은 이미 진행 중(epoch 당 ≈ 18~20 s, 체크포인트당 약 6 h).

## 5. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 |
|---|---|
| `common.A1C5_SKIP0 = 4480`; `analysis.load_raw` 구멍 검사 시작점 ∈ {0, 2560, 3200, 4480}; `run_manifest.py` 분할 표기 "A1C5 judging set (trials ≥ 4480)" | **구현** (Opus, 2026-09-23 12:40 CDT; 커밋은 아래 행과 함께) |
| `pair_tags.py` 수용 검사 확장: skip ≥ 4480 인 점은 (C5, −3) = 정확히 32 청크, (C5, 0)·(C2, −3) = 정확히 16 청크일 때만 유효, 그 외 **거부**(라벨이 아니라 종료); 태그마다 `meta\|stagec_ckpt_id` 의 `role=best` 와 `epoch == best_epoch` 확인, `--expect-ckpt TAG=sha` 로 DECISIONS 에 적은 sha 와 대조; `M-ours-bstar`·`R5-genie` 의 KEYS_RAW 태그 간 비트 동일 검사(기준 aug_a1) | **구현·검증** (`split_of` 점별 계획 + 4480 경계 걸침 거부, `check_ckpt`, `accept` 모드(+ b\*·genie 실패 수 출력); selftest, 기존 A1s2 group·A1s3 pair 출력 재현(헤더 환경 줄 제외 동일), 개발 태그로 accept·sha 거부 확인) |
| `pair_tags.py rule3` 확장: `--aug/--ctrl` 멤버 목록(평균 = group_counts) + `--decision <cell> <snr×3>` (C5 −3 0 3) → 점별 PRIMARY, ≥2점 승, power guard, PASS / NOT PASSED / guard UNDECIDED 출력; 테스트 집합 [0, 2560) 전체만 수용 | **구현** (`rule3 --aug/--ctrl` 멤버 목록 = group_counts, 1멤버는 기존 pair 와 동일; `--decision` 은 `--expect-ckpt` 필수, 결측·무효 점 거부; 기존 헤드라인 쌍으로 pooled 454:78 재현) |
| `conf/code/run_a1c5.sh`: `A1C5_TRAIN_DONE` 확인 → 4개 last 파일의 `stopped_by`·`aborted`·best/last epoch 일치를 읽어 자격을 판정하고 6 체크포인트 identity(sha, epoch)를 `DECISIONS.md` 에 기록 → 6 태그 × 3점 실행 → manifest → `pair_tags.py group` (H9 = `--aug a2 a3 --ctrl a2 a3`; 보고용 3쌍·쌍별) | **구현** (`run_a1c5.sh`: 깨끗한 코드 트리 확인, identity 커밋 실패 시 중단, 재실행 시 identity 재기록 없음, 빈 GPU 만 사용, 3 태그씩 192 워커, H9 는 `--h9` 로만(그 외 group 출력은 '부차 (보고, 판정 아님)'); 적대적 코드 검토 wf_fa31d00f-f4a 반영) |
| `conf/code/a1c5_report.py` (GB′, B16e4k kron K=1024 assert) + `diag_p1_heldout.py --ckpt … --out …` 호출 (보고 전용) | **구현** (`ckpts`: 쌍 자격·identity → `a1c5_ckpts.json` + DECISIONS, a1 은 등록 sha 로 대조; `gbprime`: a1 aug 로 시험 8 s, 시험 산출물은 삭제) |
| a2·a3 학습 | **완료** (09:38 CDT~; 종료 ctrl_a2 15:01, ctrl_a3 16:23, aug_a2 17:09, aug_a3 17:14 CDT; 넷 다 patience, aborted=False; best epoch 1037 / 1426 / 1444 / 1320) |
| 판정 실행 | **완료** (자격·identity 커밋 57709965 17:15 CDT → 평가 17:15~17:25 CDT, 코드 710a5a3f; 수용 검사 통과) — **H9 판정 불가** → §2 에 따라 A1 닫음, 테스트 확증 없음. 수치는 §6 |

## 6. 판정 결과 (2026-09-23 17:25 CDT, `run_a1c5.sh` @710a5a3f; 이 절은 추가만 한다)

**자격·identity** (평가 전 커밋 57709965, `a1c5_ckpts.json`, DECISIONS 같은 시각): 6개 모두 자격 있음. aug_a2 sha256[:16] 3f3639584bc626e7 (_best epoch 1444, last 1464), aug_a3 646926eb5f77b25d (1320 / 1340), ctrl_a2 a45fdf61281dfcc6 (1037 / 1057), ctrl_a3 23ed9e6db8d865f7 (1426 / 1446); a1 은 등록값(40c55cb294340594 / e2b22673ac91ed8f). 넷 다 `stopped_by=patience`, `aborted=False`.

**수용 검사 통과** (`A1C5_accept_C5.txt`, `A1C5_accept_C2.txt`): 세 점 모두 등록 계획(32 / 16 / 16 청크), run 파라미터 동일, 태그마다 role=best·epoch==best_epoch·sha 일치, `M-ours-bstar`·`R5-genie` 의 KEYS_RAW 가 6 태그 간 비트 동일(기준 aug_a1).

### 6.1 판정점 C5 −3 dB (n = 1280, 시행 4480..5759)

| 체크포인트 | a1 | a2 | a3 |
|---|---|---|---|
| aug V1 실패 | 528 | 517 | 518 |
| ctrl V1 실패 | 526 | 524 | 519 |

맥락(태그 간 동일): GMM b\* 642, genie 59.

- **H9 (a2·a3 2쌍 평균)**: 평균 실패 aug 517.5 vs ctrl 521.5, d = 0 제외 1139, **a:b = 70:71, n_d 141, p = 1, MDD 25 → 판정 불가** (`A1C5_H9_C5_m3.txt`).
- 부차(보고): a1 쌍 새 시행 재현 **528 vs 526, 47:45, p = 0.92** — 개발 집합의 16:38(p = 0.0038)은 새 시행에서 재현되지 않았다. a2 쌍 42:49 (p = 0.53), a3 쌍 50:51 (p = 1); 새 2쌍 중 aug 가 적은 쌍 2/2, p < 0.05 인 쌍 0/2. 3쌍 group 78:77 (p = 1).

### 6.2 보고 전용 점 (n = 640, 시행 4480..5119; 판정 아님)

| 점 | V1 실패 aug a1/a2/a3 | ctrl a1/a2/a3 | 2쌍 group (a2·a3) | 3쌍 group | a1 쌍 | b\* / genie |
|---|---|---|---|---|---|---|
| C5 0 dB | 94 / 97 / 85 | 104 / 92 / 92 | 24:24, p = 1 | 28:34, p = 0.53 | 14:24, p = 0.14 | 133 / 9 |
| C2 −3 dB | 103 / 100 / 98 | 100 / 100 / 99 | 13:13, p = 1 | 18:17, p = 1 | 11:8, p = 0.65 | 170 / 27 |

*(2026-09-23 17:36 CDT 추가(커밋 6d56404a; 처음 17:45 로 잘못 적음) — 기록 감사 wf_f3d78aff-f51: §1 부차 (2) 를 보고 전용 점에도 적는다)* 쌍별: C5 0 dB a2 19:14 (p = 0.49), a3 11:18 (p = 0.26) — aug 가 적은 쌍 1/2, p < 0.05 인 쌍 0/2; C2 −3 dB a2 8:8 (p = 1), a3 8:9 (p = 1) — 1/2, 0/2 (`A1C5_rep_group2_{C5_0,C2_m3}.txt`, `A1C5_rep_pair_a{2,3}_*.txt`).

### 6.3 보고 전용 지표 (GPU; 판정에 쓰지 않음)

| 체크포인트 | GB′ worst excess (V1 대 b\* kron K=1024) | ε_φ 위상 비 (low / mid / high, held-out) |
|---|---|---|
| aug_a1 | −12.37% | 0.2299 / 0.1406 / 0.0758 |
| aug_a2 | −12.32% | 0.2335 / 0.1396 / 0.0768 |
| aug_a3 | −12.40% | 0.2283 / 0.1382 / 0.0745 |
| ctrl_a1 | −12.19% | 0.2486 / 0.1509 / 0.0824 |
| ctrl_a2 | −12.46% | 0.2432 / 0.1494 / 0.0812 |
| ctrl_a3 | −12.35% | 0.2428 / 0.1469 / 0.0789 |

(`gbprime_review_next_A1C5_*.txt`, `p1_heldout_review_next_A1C5_*.{txt,npz}` — 비등록 ckpt 라 "NOT A VERDICT"; 참고로 헤드라인 레거시 ckpt 의 P1 값 0.246 / 0.148 / 0.083.) 위상 비는 세 쌍·세 구간 모두 aug 가 작다.

### 6.4 §2 에 따른 결과

H9 = 판정 불가 → **A1 은 "개발 집합 보고 전용 신호, 새 학습 쌍의 새 시행에서 재현되지 않음(판정 불가)" 으로 닫는다.** 테스트 집합 확증은 발동하지 않는다. a1 쌍의 재현 결과(47:45)는 보고로만 남는다. 헤드라인·v3 의 2·3단계 판정은 바뀌지 않는다.

### 6.5 §3 예측 대조 (빗나간 것도 그대로)

| 예측 | 결과 |
|---|---|
| H9: 지지, net(a−b) = −30 ~ −90 | **빗나감** — net −1, 판정 불가. §3 에 적은 대안 시나리오("group net ≈ 0, 판정 불가")와 같다. 다만 대안 시나리오의 이유로 적은 "a1 의 신호가 초기값 운" 은 a1 쌍 자체가 새 시행에서 재현되지 않아(47:45) 지지되지 않는다 |
| 부차: a1 쌍 재현 net −20 ~ −60, p < 0.05 | **빗나감** (net +2, p = 0.92) |
| 부차: 새 2쌍 각각 aug 가 적음(2/2), p < 0.05 인 쌍 1~2 | 방향 2/2 **적중**(−7, −1), p < 0.05 쌍 0 **빗나감** |
| 부차: 3쌍 group 지지 | **빗나감** (78:77) |
| 보고: C5 0 dB 는 aug 가 적지만 판정 불가 | 2쌍 group 24:24(같음) — "aug 가 적음" 은 **빗나감**, 판정 불가는 적중; 3쌍 group 28:34 는 aug 가 적고 판정 불가 |
| 보고: C2 −3 dB 판정 불가 | **적중** (13:13, 18:17) |
| GB′: aug ≈ ctrl (1%p 이내) | **적중** (−12.19 ~ −12.46%) |
| ε_φ: aug < ctrl | **적중** (세 쌍·세 구간 모두) |
