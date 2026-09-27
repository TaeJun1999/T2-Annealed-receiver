# NEXT_EXPERIMENTS_MISMATCH16e4 — 학습/평가 채널 모델 불일치: 한 채널 모델로 학습한 V1·b\* 를 다른 채널 모델의 테스트 시행에서 (8 쌍) (사전 등록 v2)

- 작성: 2026-09-26 22:54 CDT (= 2026-09-27 12:54 KST) 초안 v1, Claude Code (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 1·권고 9; `prereg_reviews_2026-09-26/review_MISMATCH16e4.md`) 반영 v2 2026-09-26 23:17 CDT (Opus 5.5). 동결 시각 = 커밋 시각(`DECISIONS.md` 같은 줄). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_PILOT16e4.md` (같은 시행·다른 arm raw 의 쌍 비교, 무결성 선행), `NEXT_EXPERIMENTS_{D3B16e4,SVB16e4,38901}.md` (UNGATED 측정 라벨), `08_SPEC_analysis.md` §2 표 B.
- **작성 시점 공개**: 사용자의 "추가 실험" 질문에 대한 선택("1 불일치 강건성", 응답 시각 미기록; 링크 생성 22:49 CDT 이전)으로 쓴다. 평가 prior 5 개(D2 S2, D3 S2c, SV8e, UMi28, MIX3)의 **정합(matched) 결과를 모두 본 뒤**다(§0). 파일럿 전용 등록(PILOT16e4)의 실행이 진행 중이며 그 라벨은 이 초안 작성 때 **읽지 않았다**(pair 파일 머리말의 무결성 줄만 봄). 불일치 조합의 BLER 은 한 번도 돌지 않았다. 스모크 기록: (1) 링크 생성(22:49 CDT) 뒤·코드 변경 전, `runner.py smoke --testbed D2 --cell C2 --ntrain 160000 --prior {S2c | S2 | UMi28} --stagec-ckpt ckpt/{d2sx_N160000_a1.pt | d2sx_UMi28_N160000_a1_best.pt | d2sx_N160000_a1.pt} --tag {MMs2s2c | MMu28s2 | MMs2u28}` 3 건이 runner 의 prior 불일치 거부로 **빌드 전에** 멈췄다(첫 호출은 출력 필터 탓에 메시지가 안 보였고, MMs2s2c 를 필터 없이 다시 불러 거부 문구를 확인; 시각 미기록, 로그 파일 없음 — §1 코드 변경의 이유). (2) 코드 커밋 7c6ebcda 뒤 가드 4 경우 스모크(§1): 등록형 MMs2s2c 는 n=2 로 빌드·실행(수치 버림), 나머지 3 경우 거부. 빈 `raw_MM*` 디렉터리는 지웠다. 쌍 선택은 §1 에 이유와 함께 고정하며, SV8e 쌍은 정합 SV8e 가 (iv) 였던 것을 **알고도** 포함한다(빼면 선택 편향이 되므로).
- 목적: 리뷰어 질문 "학습 prior 는 학습 분포 밖에서 무너지지 않는가; 불일치 아래에서도 같은 불일치를 겪는 GMM 보다 나은가" 에 답한다. 두 prior 가 **같은 학습 채널 집합**(학습 prior 의 N′=1.6e5)에서 온 것을 그대로 쓰므로 불일치는 둘에게 같다. 헤드라인과 기존 등록 판정은 어느 결과에서도 바뀌지 않는다.

---

## 0. 정합 출발점 (판정에 쓰지 않는다; 각 평가 prior 의 base raw, BLER@16 실패 수 / 2560, SNR −3..15 dB)

| 평가 prior (base raw) | 정합 표 B `b* → V1` (판정점) | R2 | b\* | V1 | genie | 정합 SNR@0.1 격차 b\*−V1 |
|---|---|---|---|---|---|---|
| D2 S2 (`raw_B16e4k`) | (i) 3/3 (−3/0/+3) | 839 261 97 57 31 29 15 | 623 184 57 28 17 16 8 | 371 88 29 16 7 5 3 | 87 26 12 9 2 2 2 | +1.41 [+1.22, +1.64] |
| D3 S2c (`raw_D3B16e4`) | (i) 3/3 (0/+3/+6) | 1454 749 304 199 75 57 22 | 1298 586 226 111 53 36 12 | 1000 404 129 64 27 22 5 | 485 149 47 35 10 14 3 | +1.41 [+1.19, +1.67] |
| SV8e (`raw_SVB16e4`) | (iv) (−3/0 두 점) | 599 82 15 2 0 0 0 | 464 60 7 0 0 0 0 | 402 46 5 0 0 0 0 | 31 3 0 1 0 0 0 | +0.25 [+0.16, +0.33] |
| UMi28 (`raw_U28B16e4`) | (i) 3/3 (+3/+6/+9) | 1458 861 574 334 172 80 48 | 1270 714 431 243 126 69 27 | 1228 656 393 215 104 44 24 | 594 302 131 58 26 8 3 | +0.60 [+0.33, +0.87] |
| MIX3 (`raw_MXB16e4`) | (i) 3/3 (+3/+6/+9), 보고 전용 | 1613 1065 641 378 214 103 49 | 1421 844 425 243 135 58 16 | 1354 789 379 193 104 41 17 | 679 358 143 68 35 13 2 | +0.98 [+0.68, +1.31] |

모든 prior 의 학습 채널은 같은 전력 정규화다(표본 공분산 trace/N = 1.0004 / 1.001 / 0.9996 / 1.0 / 1.0; S2 / S2c / SV8e / UMi28 / MIX3). 따라서 불일치는 구조(경로 수·이득 분포·군집·시나리오)의 불일치이지 척도의 불일치가 아니다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **코드 변경 (동결 커밋 이전의 별도 커밋, 해시는 §5)** | 커밋 **7c6ebcda**: `runner.py` 의 "D3 review R1" 거부(체크포인트의 학습 prior ≠ 실행 prior 이면 종료)에 **명시적 옵트인** `--train-prior P` (choices = common.PID) 를 더한다: `--train-prior` 가 체크포인트의 `prior` 와 같고 실행 prior 와 다를 때만 통과, `--stagec-ckpt`·`--tag` 필수, 그리고 태그 fits 의 full K=32 파일 **실경로 이름이 `fit_<학습 prior>_`** 로 시작해야 한다(반쪽 불일치 차단). 그 밖에는 기존대로 거부. 수신기·arm·통계 코드는 바뀌지 않는다(`git diff d63b26be 7c6ebcda -- conf/code/runner.py` = 인자·가드 20 줄). 가드 스모크 4 경우: 등록형(MMs2s2c) 통과, 정합 실행 + 플래그 거부, 플래그 없는 불일치 거부, 태그 fits 가 평가 prior 파일(PILD3)이면 거부. UMi28 시드 s2 (SEEDS16e4) 는 이 커밋 뒤 코드로 돌며 그 등록의 `--ref-arms all` 검사가 수신기 불변을 따로 확인한다 |
| **불일치 구성** | 평가 태그의 fits 디렉터리 `results/gmm_fits_D2_<TAG>/` = **학습 prior 의 적합 파일을 평가 prior 이름으로 연결한 링크**(`fit_<P_te>_Nr8_<fam>K<K>_n160000.npz → ../gmm_fits_D2_<학습 base>/fit_<P_tr>_…`; 학습 prior 의 격자 전부). 따라서 b\* 선택(검증 LL 최대)·GMM 매개변수·표본 공분산 Chat(R2 와 V1 의 C/cbar)이 **모두 학습 prior 의 것**이고, 확산 체크포인트도 학습 prior 의 판정 가중치다. 시행(채널·잡음·비트)은 평가 prior 의 테스트 스트림(`trial_rng(D2, P_te, 8, 16, 4, SNR)`) — 평가 prior 의 base raw 와 시행 단위로 짝지어진다. **불일치의 범위**: prior 쪽(확산 가중치·GMM·Chat·b\* 의 K 선택 = 학습 prior 검증 우도)만 불일치이고, 파일럿 행렬은 평가 prior 의 것(송신기 측 eig 파일럿; base 와 같아야 짝지어진다), 잡음 분산 σ² 는 수신기가 안다. σ 격자는 체크포인트의 sigma_tag 로 정해진다(학습 prior 의 것). R5-genie 는 H 와 σ² 만 쓰므로 Chat 이 바뀌어도 비트 동일해야 하며, 그 동일성은 **같은 시행**의 증명이지 prior 의 증명이 아니다 |
| **8 쌍 (학습 → 평가)** | 아래 §1a. 선택 이유: (가) 같은 기하·다른 이득 법칙 D2↔D3, (나) 같은 표준 모델의 시나리오 부분/상위 집합 UMi28↔MIX3, (다) 합성 ↔ 3GPP 표준 D2↔UMi28, (라) 합성 두 모델 D2↔SV8e. 방향 둘 다. 5 prior 의 순서쌍 20 개 중 나머지 12 개(SV8e↔D3·SV8e↔UMi28 등)는 D2 를 허브로 한 설계로 뺐고, **이 등록으로 나중에 추가하지 않는다**(추가하려면 새 등록). §6 은 8 개 pair 파일(또는 무효 기록)이 모두 있을 때만 쓴다 |
| **arm** | `M-ours-dscore-C-V1` (V1), `M-ours-bstar` (b\*), `R2-ours-G` (같은 수신기의 Gaussian prior), `R5-genie` (시행 동일성 확인용). 분석에서 불일치 arm 은 `V1-mis`, `bstar-mis`, `R2-mis` 로 이름을 바꾸어 정합 arm(base raw)과 합친다 |
| **실행 (명령 원문)** | `bash code/run_mismatch16e4.sh` (8 쌍 순차). **8 개 전부 실행·보고한다.** 인자 부분집합은 중단된 쌍의 **재개에만** 쓰며(모르는 이름이면 중단), 어떤 쌍도 결과를 본 뒤 빼지 않는다. 스크립트 안: `export CUDA_VISIBLE_DEVICES=` (GPU 숨김; UMi28·MIX3 평가 prior 필수), `conf/code`·`Demo` dirty 면 중단, fits 디렉터리·ckpt sha 확인 → `runner.py run --testbed D2 --prior <P_te> --cell C2 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt <학습 ckpt> --train-prior <P_tr> --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie --tag <TAG>` (로그 `logs/run_D2_<TAG>.log`) → `run_manifest.py --tag <TAG>` → `eval_accept.py` (`results/review_next/<TAG>_accept.txt`) → 수용 통과 시에만 `pair_mismatch.py` (`results/review_next/pair_<TAG>.txt`). CPU complex128, C2 (8×4, T=16, Tp=4), 7 SNR, 테스트 시행 0..2559, chunk 40, 16 반복. 로그 `logs/run_mismatch16e4.log`, 끝 표시 `MISMATCH_EVAL_DONE ok=<n> fail=<n>` |
| **수용 검사 (쌍마다)** | (a) `eval_accept.py --prior <P_te> --tag <TAG>:<role>:<sha>:C2 --ntrain 160000 --bstar <학습 b\*> [--kron-K K] --ll-val <학습 b\* ll_val> --ref-raw <평가 base raw>` → 청크 계획, meta 의 b\*·K·ll_val = **학습 prior 의 값**(= 불일치 적합을 실제로 읽었다는 증거), ckpt sha·role = 학습 체크포인트, iters 16, **R5-genie 가 평가 base raw 와 모든 시행·반복에서 비트 동일**. (b) 스크립트 사전 검사: base raw·학습 base raw 존재, 태그 fits 의 **모든 링크가 `readlink -e` 로 풀리고 실파일 이름이 `fit_<학습 prior>_Nr8_`** (13 개 이상). (c) `pair_mismatch.py --train-base <학습 prior 의 base raw> --train-prior <P_tr>` 무결성: 점 집합 = base = 7 SNR, `load_raw` 경고 없음, genie 4 키 동일, **학습 적합 지문**: 불일치 태그의 meta `em_sec` 와 모든 `ll_val|*` (gmm16..512·kron; `ll_val|gmm32` 는 Chat 이 든 npz 의 지문) = 학습 base raw 의 값, **불일치 적용 확인**: bstar-mis·R2-mis 의 nmse 가 정합 arm 과 비트 동일이 아님(두 arm 모두 예외 없는 시행에서). 실패 시 라벨 전에 rc=1. (a)·(b)·(c) 중 하나라도 실패하면 그 쌍은 **무효**(판정 없음, 원인 기록, 재실행은 사용자 승인). 예외 시행: 블록 오류로 유지(01_RULES §4), 개수를 pair 파일 머리말에 보고 |
| **비교 (표 B 규칙 그대로; 첫째 = 앵커)** | **MM**: `bstar-mis → V1-mis` (같은 불일치 아래 GMM 대 V1; 앵커 bstar-mis) — 쌍마다 **측정 라벨**. 보고 전용(라벨 출력, 판정 아님): `V1-mis → V1(정합)` (V1 의 불일치 비용), `bstar-mis → b*(정합)` (GMM 의 불일치 비용), `b*(정합) → V1-mis` (불일치 V1 대 정합 GMM), `R2-mis → V1-mis`, `R2-mis → R2(정합)` |
| **판정 층위·다중성** | 8 개 MM 라벨은 모두 **측정 라벨**(체크포인트는 D2 헤드라인 외 UNGATED 이고, D2 체크포인트도 D2 이외 채널에서는 게이트가 말하는 바가 없다). 데이터셋 간 집계는 **개수 서술만**("8 중 k 에서 (i)"). 1차 검정 없음; 보고 전용 pair 40 개(쌍당 5 × 8); 등록 사이 보정 없음 |
| 보고 전용 | 비교마다 SNR@0.1 격차(90% paired bootstrap, `analysis.gain`, seed 20260925), 판정점 부호검정 a:b; SNR 별 실패 수(R2-mis, bstar-mis, V1-mis, 정합 R2, b\*, V1, genie). 불일치 비용 비교 "V1 의 SNR@0.1 손실(V1-mis − V1) 대 b\* 의 손실(bstar-mis − b\*)" 는 두 격차를 나란히 적을 뿐 차이 검정은 하지 않는다; 격차 보존율 = 격차(bstar-mis − V1-mis) / 정합 격차(b\* − V1) (점추정만); SNR 별 채널 추정 NMSE@16 중앙값(R2-mis, bstar-mis, V1-mis, 정합 셋) |
| 비용 | CPU 만. 쌍당 4 arm × 448 청크(V1 이 지배적) — 정합 14 arm 실행(쌍당 30–70 분)의 ¼ 안팎 → 쌍당 ≈ 10–20 분, 8 쌍 ≈ 2 h. GPU·학습 없음 |

### 1a. 쌍 표 (b\* = 학습 prior 의 것; N′ = 1.6e5)

| 이름 | TAG | 학습 prior (체크포인트, sha, role) | 학습 b\* (ll_val) | 평가 prior (base raw) | fits 링크 수 |
|---|---|---|---|---|---|
| D2-D3 | MMs2s2c | S2 (`d2sx_N160000_a1.pt`, 4443921ce8d5c4a1, legacy-last) | kron 1024 (−11.459169831224418) | S2c (`raw_D3B16e4`) | 13 |
| D3-D2 | MMs2cs2 | S2c (`d2sx_S2c_N160000_a1_best.pt`, 7ebf4e6647d4413f, best) | kron 4096 (0.08879931165293979) | S2 (`raw_B16e4k`) | 15 |
| U28-MX | MMu28mx | UMi28 (`d2sx_UMi28_N160000_a1_best.pt`, 6f3a1b9490864af1, best) | kron 4096 (5.797910431000217) | MIX3 (`raw_MXB16e4`) | 15 |
| MX-U28 | MMmxu28 | MIX3 (`d2sx_MIX3_N160000_a1_best.pt`, b591ae24ae3c5f31, best) | kron 4096 (33.7604873920761) | UMi28 (`raw_U28B16e4`) | 15 |
| D2-U28 | MMs2u28 | S2 (`d2sx_N160000_a1.pt`, 4443921ce8d5c4a1, legacy-last) | kron 1024 (−11.459169831224418) | UMi28 (`raw_U28B16e4`) | 13 |
| U28-D2 | MMu28s2 | UMi28 (`d2sx_UMi28_N160000_a1_best.pt`, 6f3a1b9490864af1, best) | kron 4096 (5.797910431000217) | S2 (`raw_B16e4k`) | 15 |
| D2-SV | MMs2sv | S2 (`d2sx_N160000_a1.pt`, 4443921ce8d5c4a1, legacy-last) | kron 1024 (−11.459169831224418) | SV8e (`raw_SVB16e4`) | 13 |
| SV-D2 | MMsvs2 | SV8e (`d2sx_SV8e_N160000_a1_best.pt`, d2d78962c2846364, best) | full gmm256 (−47.80545576704972) | S2 (`raw_B16e4k`) | 14 |

## 2. 라벨 (MM, 쌍마다; UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

| 표 B `bstar-mis → V1-mis` | 기록 |
|---|---|
| (i) POWERED, second arm fewer ≥ 2/3 | "학습 <P_tr> → 평가 <P_te> 불일치 아래 V1 이 b\* 보다 적게 실패" |
| (ii) POWERED, first arm fewer ≥ 2/3 | "같은 불일치 아래 b\* 가 V1 보다 적게 실패" |
| (iii) POWERED, 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" |
| (iv) UNDECIDED | "판정하지 못함 (검정력 미달)" — 격자·시행 확장 없음 |
| 무효 | 판정 없음, 원인 기록 |

- 문장은 "이 학습 → 평가 조합, 이 셀·예산" 한정이다. "V1 은 분포 이동에 강건하다" 같은 일반 문장은 쓰지 않는다; 쓰는 것은 "8 조합 중 k 에서 같은 불일치의 b\* 보다 적게 실패" 와 조합별 불일치 비용(보고)이다.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; §0 을 본 뒤의 예측; 항목마다 적중/빗나감 이분)

1. D2-D3, D3-D2: MM **(i)** 둘 다 (같은 기하; 한 항목, 2/2 일 때만 적중).
2. U28-MX, MX-U28: MM **(i)** 둘 다 (시나리오 부분/상위 집합; 한 항목, 2/2).
3. D2-U28, U28-D2: MM **(i) 아님** 둘 다 (합성 ↔ 표준의 큰 불일치에서 학습 prior 가 유리하다는 근거 없음; 한 항목). 채점: 쌍마다 (ii)/(iii) = 적중, (i) = 빗나감, (iv) = 채점 불가; 둘 다 적중일 때만 항목 적중, 하나라도 빗나가면 빗나감, 그 밖은 채점 불가.
4. D2-SV, SV-D2: 예측 없음(정합 SV8e 가 (iv); 방향 근거 없음) — 기록만.
5. 보고 `V1-mis → V1(정합)`: 8 쌍 모두 (i) (불일치가 V1 에 비용을 부과; 한 항목, 8/8).
6. 보고 `b*(정합) → V1-mis`: D2-D3 과 D3-D2 에서 (i) (불일치 V1 이 정합 b\* 보다 적게 실패; 정합 격차 +1.41 dB 가 불일치 비용보다 크다는 약한 예측; 한 항목, 2/2).
7. 빗나갈 경로: (a) 불일치 적용 검사 실패(정합 적합을 읽음) → 무효·원인(링크) 기록; (b) 큰 불일치에서 V1 이 R2-mis 보다도 나쁨 → 그대로 기록, 한계 절.

## 4. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 |
|---|---|
| fits 링크 디렉터리 8 개 `results/gmm_fits_D2_MM*` | 생성됨(6 개 22:49 CDT, SV8e 2 개 22:54 CDT — 디렉터리 mtime; 커밋 대상 아님) |
| `code/pair_mismatch.py` | v1 자체 검사: 시드 태그 raw(불일치 없음)로 rc=1 거부, 정합 arm 으로 만든 가짜 raw 로 헤드라인 표 B 재현(302:50·117:21·35:7, (i)). v2(검토 반영) 자체 검사: 같은 가짜 raw + 올바른 학습 base(raw_B16e4k, S2) 로 통과(격차 보존율 1.00), 틀린 학습 base(raw_D3B16e4, S2c) 로 지문 불일치 rc=1 |
| `code/run_mismatch16e4.sh` | 작성(`bash -n` OK) |
| `runner.py --train-prior` | PILOT16e4 실행 종료(23:07 CDT) 뒤 수정·가드 스모크 4 경우·커밋 7c6ebcda |
| run_manifest 에 학습 prior 항목(검토 권고 3) | 넣지 않음: SEEDS16e4 의 실행 중 체인이 run_manifest 를 부르므로 등록 실행 중 코드를 바꾸지 않았다. 출처는 raw meta `stagec_ckpt`(학습 체크포인트 경로)·`stagec_ckpt_id` 와 (c) 의 학습 적합 지문으로 증명된다 |
| 적대적 검토 1건(Fable) → v2 → 동결 커밋 → BLER 8 쌍 → 수용·무결성 → §6 | v2 반영 완료(이 커밋 = 동결) |

## 5. 평가 전 고정 기록

| 항목 | 값 |
|---|---|
| `--train-prior`·`pair_mismatch.py`·`run_mismatch16e4.sh` 코드 커밋 | 7c6ebcda (동결 커밋에서 코드 변경 없음) |
| 동결 커밋 | [DECISIONS 줄에] |

## 6. 결과 (이 절은 추가만 한다)
