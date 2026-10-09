# NEXT_EXPERIMENTS_SITE16e4 — 헤드라인 셀의 V4 → V1 짝 검정 (기존 raw 의 표 B; 규칙 고정 사후 계산, 등록 v2)

- 작성: 2026-10-08 22:37 CDT (= 10-09 12:37 KST) 초안 v1 (Opus 5.5, 서버 세션) → 적대적 검토 1 건 (Fable 5.1 서브에이전트, 검토 파일 2026-10-08 22:50 CDT; MUST 2·SHOULD 7·NIT 7, 등록 쌍의 사전 누출 없음; `prereg_reviews_site16e4/review_SITE16e4.md`) → **v2** (2026-10-08 22:54 CDT (= 10-09 12:54 KST), Opus 5.5; 아래 'v1 → v2') → 동결 커밋 (`DECISIONS.md` 의 같은 날 줄). 동결 뒤 §0–§3 을 바꾸지 않는다.
- 틀: `08_SPEC_analysis.md` §2 (표 B: paired sign test, 검정력 하한), `NEXT_EXPERIMENTS_STATIC16e4.md` 의 형식과 지위 (기존 raw 위의 규칙 고정 사후 계산; `--provenance manifest`), `code/pair_baselines.py` (`table_b` — `analysis.decision_points`·`paired`·`sign_p`·`gain` 을 그대로 부른다).
- **사용자 결정** (2026-10-08 22:21 CDT, "검정은 해보자"; 웹 채팅이 옮긴 프롬프트): (1) **원고 반영** — 결과가 어떻든 §2 의 해당 문장을 ICC 원고 IV-F 에 넣는다; 결과를 본 뒤 넣을지 고르지 않는다. (2) **범위** — 헤드라인 셀 하나 (D2 C2 8×4, N′ = 1.6e5, `raw_B16e4k`); C6 (16×4)·다른 예산·다른 쌍은 하지 않는다.
- **작성 시점 공개 (중요)**: 이 등록은 **새 BLER 을 돌리지 않는다** — 기존 raw 위의 계산이다. 프롬프트 작성자 (웹 채팅)·사용자는 두 arm 의 BLER 표 (`results/tables_D2_B16e4k.txt`) 와 아래 두 기록 쌍을 이미 봤다. 기록자 (이 서버 세션) 가 이 문서를 쓰기 전에 본 것: 프롬프트의 §0 수치; `results/tables_D2_B16e4k.txt` :64–74 (TABLE A 의 BLER 행) 와 :336–380 (표 B 의 `R2-ours-G →`·`M-ours-bstar →` 쌍); `results/review_next/pairB_STB16e4k.txt` 의 머리말 3 줄과 실패 수 블록 :102–118 (V4 줄은 그 블록에 없다); `tables_D2_B16e4k.txt` :403 의 쌍 머리줄 (`V4 → R5-genie`; 검토가 지적해 머리줄만 확인, 수치는 열람하지 않음); 동결 전 회귀·스모크 출력 (§4 — `b* → V1`·`b* → V4` 만); 적대적 검토 파일. **V4 ↔ V1 의 짝 수량 (불일치 쌍 수, p, bootstrap 구간) 은 누구도 계산·열람하지 않았다** (어느 표에도 없다 — `docs/paper/CONTRIBUTIONS.md` §0 :34; §4 의 회귀·스모크는 이 쌍을 계산하지 않았다). 따라서 지위는 STATIC16e4 와 같은 **"규칙 고정 사후 계산"** 이며 "사전 등록" 이라 부르지 않는다.
- **주변 실패 수만으로 이미 정해져 있는 것 (판정 전 공개)** — §0 의 실패 수는 공개돼 있고, 짝 검정의 a − b 는 두 arm 의 실패 수 차와 같다:
  - (a) 점별 a − b = F_V4 − F_V1 = **+23 / +8 / −8** (−3 / 0 / +3 dB), pooled a − b = **+23** (a = V4 만 실패, b = V1 만 실패).
  - (b) SNR@0.1 격차의 **점추정**은 두 arm 의 주변 BLER 곡선만의 함수다 (`gain`: arm 별 `snr_at` 의 차) → 두 기록 격차의 차 1.41 − 1.27 ≈ **+0.14 dB** (각 기록값의 반올림 때문에 ±0.01).
  - (c) **라벨 (ii) 와 (iv) 는 나올 수 없다.** (ii) 는 V4 쪽 방향 (b > a) 이 +3 dB 한 점뿐이라 "2 점 이상" 이 불가능하다. (iv) 는 불일치 쌍 수 D = a + b ≥ |a − b| = 23 / 8 / 8 ≥ 6 이 세 점 모두라 power guard 가 반드시 통과한다.
  - (d) 라벨 (i) 은 −3 dB 와 0 dB 가 **둘 다** V1 쪽 유의일 때만 나온다. exact 부호검정에서 a − b = +8 인 0 dB 는 D ≤ 12 (10:2, p = 0.039) 일 때만 유의하고 (D = 14 → 11:3, p = 0.057), a − b = +23 인 −3 dB 는 D ≤ 125 (74:51, p = 0.049) 일 때만 유의하다 (D = 127 → 75:52, p = 0.0505). +3 dB (b − a = +8) 의 V4 쪽 유의도 D ≤ 12 일 때만이다. 두 arm 이 **함께** 실패한 블록 수 c 로 쓰면 (D = F_V4 + F_V1 − 2c): −3 dB V1 쪽 유의 ⟺ c ≥ 320 (V1 실패 371 중), 0 dB V1 쪽 유의 ⟺ c ≥ 86 (V1 실패 88 중), +3 dB V4 쪽 유의 ⟺ c ≥ 19 (V4 실패 21 중), pooled (보고 전용) p < .05 ⟺ pooled D ≤ 125 ⟺ Σc ≥ 437 (최대 480).
  - (e) 기록된 제 3 arm 쌍 (b\*·R2·genie) 은 V1∩V4 겹침 c 를 c(−3 dB) ≥ 36 (= 321 + 338 − 623), c(0)·c(+3) ≥ 0 으로만 묶는다 (임계 320 / 86 / 19 와 무관) → (a)–(d) 밖에 더 정해진 것은 없다.
  - **혼합 결과는 닿을 수 있다**: 같은 가중치에 site 만 다른 두 arm 이라 +3 dB 에서 V4 의 실패 21 개가 거의 전부 V1 의 실패에 들 수 있고 (c ≥ 19), 그러면 +3 dB 는 V4 쪽 유의다. 그 경우에도 라벨과 §2 문장은 규칙대로이며 문장을 더 만들지 않는다 (§2; 사용자에게 알림 — 이 세션의 메시지, 적대적 검토 뒤·동결 전; 답을 기다리지 않고 이 규칙으로 동결한다).
  - 따라서 **열려 있는 것은 점별 불일치 쌍 수 D (→ 점별 p, 라벨 (i) 대 (iii), pooled p) 와 SNR@0.1 격차의 bootstrap 구간 둘뿐**이다.
- 목적: ICC 원고 IV-F 는 V4 (같은 헤드라인 네트워크에 등방 site 만; 원고 이름 scalar-site diffusion prior) 도 b\* 보다 적게 실패한다 (438:85, +1.27 dB [+1.08, +1.50]) 고 쓰고 이득을 "module H 의 학습 prior" 로 돌리는데, V1 ↔ V4 의 직접 짝 비교는 어느 표에도 없다. 그 한 쌍을 표 B 형식으로 한 번 계산해 §2 의 고정 문장으로 적는다. **어느 결과도 헤드라인·기존 등록의 §1–§3·기존 라벨을 바꾸지 않는다.**


### v1 → v2 (검토 반영, 항목별)
| 항목 | v2 에서 한 것 | 바뀐 곳 |
|---|---|---|
| MUST-1 둘째 문장을 비울 수 있던 규칙 | 삭제. `gain` 의 kind 는 주변 BLER 로 이미 ok — 둘째 문장은 항상 채운다 (censored % 는 기록만) | §2 채우는 규칙, §3 항목 0 |
| MUST-2 "V4 가 든 기록 쌍 둘뿐" | 셋으로 정정 (`V4 → R5-genie` :403 추가); V1 과 V4 를 함께 든 쌍이 없다는 것은 그대로. `docs/paper/CONTRIBUTIONS.md` §0 :34 의 "둘뿐" 도 같은 오류 — 그 원문은 이 작업이 고치지 않는다 (결과 줄만 덧붙임), 사용자 보고에 적는다 | §0, 머리말 |
| SHOULD-1 혼합 결과 | 임계를 겹침 수 c 로도 적고, 혼합 결과가 닿을 수 있음을 머리말에 공개; 규칙은 그대로 (문장을 더 만들지 않음) 이며 사용자에게 동결 전에 알렸다 | 머리말 (d), §2, §3 |
| SHOULD-2 raised 블록 서술 | 실제 동작 (NOTE → 무결성 실패 → 라벨 없음; 이 raw 는 raised 0) 으로 고침 | §1 쌍 |
| SHOULD-3 기록 표 대조 | 스크립트가 `git show HEAD:conf/…` 와 대조, 전제에 기록 표 tracked·clean | 스크립트, §1 |
| SHOULD-4 스크립트 자기 출처 | 출력 첫 줄에 스크립트 sha256[:16]·경로; §5 에 동결 스크립트의 sha | 스크립트, §1, §5 |
| SHOULD-5 08_SPEC 쌍 목록 밖 | 다중성 행에 명시 | §1 |
| SHOULD-6 DECISIONS·WORK_QUEUE | 사용자 결정 줄·동결 줄·WORK_QUEUE 항목을 동결 커밋에 함께 | (동결 커밋) |
| SHOULD-7 제 3 arm 쌍이 겹침을 묶지 않음 | 머리말 (e) 추가 | 머리말 |
| NIT 1–7 | 0.051 → 0.0505; "같은 인자" 문구 (`--r0 at1`·`--expect` 제외); 1 단계 실패 표식; ABORT 뒤 부분 출력이 재실행을 막음을 명시; ' -> ' 개수 검사 주석; 실패 수 블록 범위 :102–118·V4 없음; x 의 0·음수 규칙은 형식상 | 머리말, §1, §2, 스크립트 |

---

## 0. 알고 있는 것 (판정에 쓰지 않는다)

| 항목 | 값 (출처) |
|---|---|
| 입력 | `raw_B16e4k` (D2 C2 8×4, prior S2, N′ = 1.6e5; 테스트 시행 0..2559, n = 2560/SNR, 7 SNR, 16 반복). V1·V4 는 같은 블록에서 같은 가중치 `ckpt/d2sx_N160000_a1.pt` (last-EMA @1784, sha256[:16] 4443921ce8d5c4a1) 를 쓴다. b\* = kron K = 1024 |
| 실패 수 @16 (−3 / 0 / +3 dB) | V1 371 / 88 / 29, V4 394 / 96 / 21, b\* 623 / 184 / 57 (아래 두 기록 쌍과 TABLE A 에서 산출; §4 스모크가 raw 에서 같은 수를 냈다) |
| BLER@16 (`tables_D2_B16e4k.txt` :71–72) | V1 0.145 / 0.034 / 0.011, V4 0.154 / 0.037 / 0.008 — 점추정은 −3·0 dB 에서 V1, +3 dB 에서 V4 가 낮다 |
| 기록된 쌍 b\* → V1 (:367–372) | 302:50 · 117:21 · 35:7, pooled 454:78, SNR@0.1 격차 +1.41 dB [90% +1.22, +1.64], 3/3 유의 |
| 기록된 쌍 b\* → V4 (:373–378) | 285:56 · 111:23 · 42:6, pooled 438:85, SNR@0.1 격차 +1.27 dB [90% +1.08, +1.50], 3/3 유의 |
| V4 가 든 기록 쌍 | `R2-ours-G → V4` (:343), `b\* → V4` (:373), `V4 → R5-genie` (:403) 셋 — **V1 과 V4 를 함께 든 쌍은 없다**; V4 는 사후 등록 변형 (`tables_D2_B16e4k.txt` :23) |
| 주변 수가 이미 정하는 것 | 머리말 (a)–(d) |

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **입력 (새 실행 없음)** | `raw_B16e4k` (위). 이 쌍의 두 arm 과 b\* 는 모두 이 base raw 에 있다. `pair_baselines.py` 가 요구하는 PIL·ALD raw (`raw_PILB16e4k`·`raw_ALDB16e4k`, 추정 `PILB16e4k`) 는 STATIC16e4 의 B16e4k 명령에서 `--r0 at1`·`--expect…` 를 뺀 인자 (R0·기록 라벨은 이 쌍과 무관) 로 주며 무결성 검사에만 쓰인다 |
| **쌍** | 표 B 형식 `M-ours-dscore-C-V4 → M-ours-dscore-C-V1` **하나**: a = V4 만 실패, b = V1 만 실패. 실패 = `blk_err[:, -1] == 1` (반복 16. raised 블록은 `load_raw` 가 1.0 으로 바꾸고 NOTE 를 내며, `pair_baselines` 는 그 NOTE 를 무결성 실패로 본다 → 라벨 없음. `raw_B16e4k` 는 무결성 OK = raised 0 이므로 `paired` 와 `fails` 가 같은 블록을 센다; 머리말 (a) 의 a − b = F_V4 − F_V1 은 이 사실에 기댄다) |
| **판정점** | **−3, 0, +3 dB 고정.** 표 B 규칙은 판정점을 쌍의 baseline 쪽 arm 에 맞춘다 (`analysis.pair_list`) — 이 쌍은 두 arm 이 모두 우리 것이라 같은 셀의 b\* 판정점 (기록 :368·:374) 을 미리 고정한다. V4 기준 자동 규칙 (BLER ∈ [0.005, 0.9], \|log10(BLER/0.1)\| 최소 셋) 도 §0 의 BLER 로 같은 셋이다 — 출력에는 확인 줄 (`check: the anchor rule on … gives …`) 만 쓰고 판정에는 쓰지 않는다 (확인 줄이 다른 셋을 내더라도 고정 판정점으로 판정하고 그 사실을 §6 에 적는다) |
| **검정** | 08_SPEC §2 그대로, 표 B 를 만든 같은 함수: 판정점마다 불일치 블록의 exact 양측 부호검정 (`exp_0921_analysis.paired`·`sign_p`), p < .05. power guard: 판정점 3 개이고 그중 2 개 이상에서 불일치 쌍 ≥ 6 (`MIN_DISC`); 아니면 UNDECIDED. 라벨 논리는 `pair_baselines.table_b` (판정점만 고정값으로 받는다 — §4) |
| **라벨** (원고 IV-A 의 정의 "p<0.05 in its favor at two or more of the three SNRs" 와 같다) | **(i) "V1 이 V4 보다 적게 실패"**: V1 쪽 유의 (a > b, p < .05) 2 점 이상 · **(ii) "V4 가 V1 보다 적게 실패"**: V4 쪽 유의 (b > a, p < .05) 2 점 이상 · **(iii) "판정하지 못함 (유의 방향 없음)"** · **(iv) "판정하지 못함 (검정력 미달)"**: power guard 미달. `table_b` 가 (iv) → (i) → (ii) → (iii) 순서로 정한다 |
| **보고 필드** | 점별 a:b·p, pooled a:b·p (보고 전용 — 라벨에 쓰지 않는다), power guard, 라벨 문자열 원문, SNR@0.1 격차 (V4 − V1) [90% paired bootstrap; 표 B 의 SNR@0.1 격차와 같은 함수·설정 = `exp_0925_analysis.gain`, B = 2000, `default_rng(20260925)`, 5–95 백분위, 같은 재표본 시행을 두 arm 에], 두 arm 의 −3 / 0 / +3 dB 실패 수 |
| **드리프트 검사 (V4 → V1 계산 전)** | 같은 코드·같은 스크립트 실행에서 `b* → V1`, `b* → V4` 를 다시 계산한다 (앵커 규칙). 부호검정 줄과 SNR@0.1 줄이 커밋본 (`git show HEAD:conf/results/tables_D2_B16e4k.txt`; 전제에서 tracked·clean 검사) 의 :369·:372·:375·:378 과 글자 단위로 같고, 실패 수 (623/184/57, 371/88/29, 394/96/21)·판정점 (−3/0/+3)·라벨 (둘 다 (i) 3/3) 이 §0 과 같아야 한다. 하나라도 다르면 **멈추고 (V4 → V1 을 계산하지 않고) 보고**한다 — `run_site16e4.sh` 가 기계적으로 |
| **무결성** | `pair_baselines` 의 검사 (STATIC16e4 §1 과 같음: 점 집합 = 셀 격자, load_raw 경고 없음, 2560 시행, genie 4 키 PIL/ALD = base, `--provenance manifest` 등) 가 어떤 수보다 먼저. 실패하면 라벨 없음 → 원인을 §6 에, 재실행은 사용자 승인 |
| **명령 (CPU, GPU 숨김; 동결 뒤 한 번)** | `bash code/run_site16e4.sh` = `CUDA_VISIBLE_DEVICES= python code/pair_baselines.py --base raw_B16e4k --pil raw_PILB16e4k --ald raw_ALDB16e4k --est PILB16e4k --cell C2 --prior S2 --provenance manifest --pairs …` 두 번: ① `"M-ours-bstar>M-ours-dscore-C-V1" "M-ours-bstar>M-ours-dscore-C-V4"` → 드리프트 검사 → ② `"M-ours-dscore-C-V4>M-ours-dscore-C-V1@-3,0,3"`. 출력 `results/review_next/pairB_SITEB16e4k.txt` (첫 줄 = 스크립트 HEAD + 스크립트 자신의 sha256[:16]·경로), 로그 `logs/run_site16e4.log` (끝 `SITE_DONE rc=`). 전제: conf/code·Demo 청결, 이 문서·`DECISIONS.md`·`results/tables_D2_B16e4k.txt` tracked·clean, HEAD = 동결 커밋 (이 문서를 마지막으로 바꾼 커밋), 출력 파일 없음. ABORT 뒤에도 부분 출력은 그대로 남아 재실행을 막는다 — 재실행은 사용자 승인 뒤 (파일을 옮기고) |
| 다중성 | 새 라벨 1 개 (보정 없음). 이 쌍은 `08_SPEC` §2 의 쌍 목록 밖이며 이 등록이 (사용자 결정으로) 하나 더한 것이다 — 검정 규칙은 08_SPEC §2 그대로이고 08_SPEC 은 바꾸지 않는다 |
| 비용 | CPU 수 분 |
| **하지 않는 것** | 새 BLER 실행, raw 수정, 다른 쌍·셀·예산 계산; 결과를 본 뒤 판정점·규칙·§2 문장 바꾸기; 헤드라인·기존 등록의 §1–§3·기존 라벨 수정 (이 결과는 어느 기존 판정도 바꾸지 않는다); ICC 원고 저장소 (T2-ICC2027-paper) 수정 |

## 2. 라벨·원고 문장 (결과 전에 고정; 원고 반영은 원고 채팅이 한다)

자리는 IV-F 의 "It attains BLER 0.1 at a 1.27\,dB [$+1.08$, $+1.50$] lower SNR." 바로 뒤다. 라벨에 맞는 첫 문장 하나와 공통 둘째 문장을 넣는다.

- (i): `In paired sign tests, the \ours{} fails less than the \scdiff{} at {two of the three | all three} tested SNRs.`
- (ii): `In paired sign tests, the \scdiff{} fails less than the \ours{} at {two of the three | all three} tested SNRs.`
- (iii)·(iv): `In paired sign tests, the comparison between the \ours{} and the \scdiff{} is not decided.`
- 공통: `The SNR gain $\Delta_{0.1}$ of the \ours{} over the \scdiff{} is {x}\,dB [${l}$, ${u}$].`
  - x = SNR@0.1(V4) − SNR@0.1(V1), 소수 둘째 자리. 구간에는 부호를 붙인다.

채우는 규칙 (기록자가 덧붙임; 결과 전 고정 — 위 문장 자체는 바꾸지 않는다):
- `{two of the three | all three}`: 이긴 쪽의 유의 점 수가 2 면 "two of the three", 3 이면 "all three". (머리말 (c)(d) 대로 이 실행에서 (ii) 와 "all three" 는 나올 수 없다.)
- x·l·u 는 `gain` 출력 문자열 `±x.xx dB  [90% paired bootstrap ±l.ll, ±u.uu; censored replicates 0%]` 의 세 수 그대로다. l·u 는 부호를 붙여 `$+0.05$`·`$-0.05$` 꼴, x 는 양수면 부호 없이 (`0.14`), 음수면 `$-$0.05` 꼴, `+0.00`·`-0.00` 이면 `0.00` (머리말 (b) 대로 x ∈ {0.13, 0.14, 0.15} 라 음수·0 은 나올 수 없다; 형식상의 규칙).
- `gain` 의 kind 는 주변 BLER 로 이미 'ok' 로 정해져 있다 (V1·V4 모두 −3 dB BLER > 0.1, 0 dB BLER < 0.1 → 두 arm 다 격자 안에서 교차; n/a·`>=` 꼴은 나올 수 없다). 둘째 문장은 **항상** 채운다. 출력의 `censored replicates` 가 `0%` 가 아니면 그 % 를 §6 과 사용자 보고에 적되 문장은 그대로 채운다.
- 혼합 (어느 한 점이 반대쪽 유의: 라벨 (i) 에서 +3 dB 가 V4 쪽 유의, 또는 라벨 (iii) 에서 −3 dB 는 V1 쪽·+3 dB 는 V4 쪽 유의) 이면 라벨과 첫 문장은 규칙대로 두고, §6 과 사용자 보고에 점별 방향을 그대로 명시한다. 이 등록은 문장을 더 만들지 않는다 — 결과 뒤에 고를 것이 없다 (원고에 더 밝히는 문구를 넣을지는 사용자의 몫이며, 이 등록의 문장을 빼거나 바꾸는 것은 아니다).
- (iii)·(iv) 를 "비긴다", "동등", "차이 없음" 으로 쓰지 않는다 — 기록·보고·원고 문장 모두.
- 원고 문장 범위: 이 셀·예산·prior (Sparse specular 8×4, N′ = 1.6e5), 판정점 −3 / 0 / +3 dB, 이미 본 BLER 표 위의 사후 형식 검정.

## 3. 미리 적는 예측 (기록자; **두 arm 의 BLER 표·실패 수를 본 뒤**의 예측임을 공개; 열린 것에 대해서만; 각 항목 적중/빗나감)

0. 이미 정해진 것 (채점 안 함): 머리말 (a)–(e) — a − b = +23 / +8 / −8, pooled +23; SNR@0.1 점추정 +0.14 ± 0.01 dB, 그 kind = ok (n/a 불가); (ii)·(iv) 불가, power guard POWERED; V4 기준 자동 판정점 = −3 / 0 / +3.
1. 라벨 = **(iii) "판정하지 못함 (유의 방향 없음)"**.
2. −3 dB: V1 쪽 유의 (p < .05) — 같은 가중치의 두 arm 이라 불일치 쌍이 적을 것이라는 추측 (D ≤ 125, 곧 c ≥ 320/371 이어야 한다).
3. 0 dB: 유의 아님 (p ≥ .05; D ≥ 14, 곧 c ≤ 85/88).
4. +3 dB: 유의 아님 (p ≥ .05; D ≥ 14, 곧 c ≤ 18/21) — 혼합 결과가 아니다.
5. pooled: p ≥ .05 (pooled D ≥ 127).
6. SNR@0.1 격차 (V4 − V1) 의 90% 구간 하한 > 0.
7. 빗나갈 경로: 무결성 실패 → 라벨 없음; 드리프트 검사 실패 → V4 → V1 미계산.

## 4. 선행 작업

| 항목 | 상태 |
|---|---|
| `code/pair_baselines.py`: `table_b(…, cand=None)` (판정점을 고정값으로 받는 선택 인자; 기본 None = 앵커 규칙, 동작 불변) + `--pairs X>Y[@S1,S2,S3]` (무결성 검사 뒤 나열한 쌍의 표 B 만 찍고 끝; baseline 루프·요약 없음; 기본값 None = 동작 불변). 찍는 줄: 쌍·판정점 (고정이면 앵커 규칙 확인값도), `sign test @16` 줄과 `SNR@0.1 gap (X minus Y)` 줄 (analysis 표 B 와 같은 꼴), `POWERED=… -> (라벨)`, 판정점의 실패 수 | 구현 (이 동결 커밋에 포함) |
| 회귀 (기본 경로 불변) | 수정한 코드로 STATIC16e4 의 B16e4k 명령을 그대로 돌린 출력 135 줄이 커밋본 `pairB_STB16e4k.txt` 의 2 행~끝과 **비트 동일** (`cmp`; sha256[:16] aa59bc15d2130592). 2026-10-08 22:33 CDT, 기록자 |
| 스모크 — **드리프트 쌍만** (V4 → V1 미계산) | `--pairs "M-ours-bstar>M-ours-dscore-C-V1" "M-ours-bstar>M-ours-dscore-C-V4" "M-ours-bstar>M-ours-dscore-C-V1@-3,0,3"`: 부호검정·SNR@0.1 줄이 `tables_D2_B16e4k.txt` :369·:372·:375·:378 과 글자 동일, 실패 수 623/184/57·371/88/29·394/96/21, 고정 판정점 경로 = 앵커 경로와 같은 수 (확인 줄 `['-3', '+0', '+3']`). 거부 2 경우 (없는 arm, 격자 밖 SNR) rc 1. 2026-10-08 22:33 CDT |
| `code/run_site16e4.sh` (v1) | `bash -n` 통과. sed 사본 (전제 줄 삭제, 출력·로그 → 세션 스크래치패드, 2 단계 쌍을 `M-ours-bstar>M-ours-dscore-C-V4@-3,0,3` 으로 바꿈 — 사본에 `V4>$V1` 문자열 0 회) 으로 흐름 확인: 드리프트 OK → 2 단계 블록 → `SITE_DONE rc=0`; 기대값 하나를 바꾼 사본 (302:50 → 302:51) 은 2 단계 전에 ABORT (rc 1, `DRIFT CHECK: FAILED -- V4 -> V1 not computed`, 출력에 step 2 줄 0). 2026-10-08 22:34 CDT |
| 스모크 산출물 | 전부 세션 스크래치패드 (저장소 밖). `results/review_next/pairB_SITE*`·`logs/run_site16e4.log` 는 동결 전 없음. **V4 → V1 수치는 어디에도 출력·열람되지 않았다** |
| 적대적 검토 (Fable 5.1 서브에이전트) | 끝남 — MUST 2·SHOULD 7·NIT 7 (`prereg_reviews_site16e4/review_SITE16e4.md`; 검토자는 기록 쌍 둘의 거부 경로만 돌렸고 등록 쌍은 계산하지 않았다 — `scratch_reject.txt`). 등록 쌍의 사전 누출: 찾지 못함 (스크래치 출력·저장소 grep) |
| `code/run_site16e4.sh` (v2: 검토 반영) | 전제에 기록 표 tracked·clean 추가, 2 차 대조를 `git show HEAD:conf/…` 로, 첫 줄에 스크립트 sha256[:16]·경로, 1 단계 실패 표식, 주석 2 곳. `bash -n` 통과; 같은 방식의 sed 사본 (전제 줄 6 개 삭제, 2 단계 쌍 = `M-ours-bstar>M-ours-dscore-C-V4@-3,0,3`, `V4>$V1` 0 회) 으로 다시 확인 — 드리프트 OK (`… lines of HEAD:conf/results/tables_D2_B16e4k.txt`) → 2 단계 블록 → `SITE_DONE rc=0` (2026-10-08 22:52–22:53 CDT). 동결되는 스크립트의 sha256[:16] = b3bee226cf046878 |
| 동결 → 실행 → §6 → 기록 감사 | 대기 |

## 5. 평가 전 고정 기록

| 항목 | 값 |
|---|---|
| 동결 커밋 | 이 문서·`code/pair_baselines.py`·`code/run_site16e4.sh`·`DECISIONS.md` 를 담은 커밋 (해시는 출력 첫 줄과 §6 첫 줄에) |
| raw·가중치 고정 | base `raw_B16e4k`: `manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520` (pair_baselines 머리말; STATIC16e4 출력과 같은 값); V1·V4 체크포인트 `d2sx_N160000_a1.pt` sha256[:16] 4443921ce8d5c4a1 |
| 드리프트 기준 줄 | `tables_D2_B16e4k.txt` :369·:372·:375·:378 (커밋본) 과 §0 의 실패 수 — `run_site16e4.sh` 의 `EXP` 8 줄 |
| 스크립트 고정 | `code/run_site16e4.sh` sha256[:16] = b3bee226cf046878 (출력 첫 줄의 값과 같아야 한다; 다르면 다른 사본이 돈 것) |

## 6. 결과 (이 절은 추가만 한다)
