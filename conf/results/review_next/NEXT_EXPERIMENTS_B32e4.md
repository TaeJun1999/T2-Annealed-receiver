# NEXT_EXPERIMENTS_B32e4 — 동일예산 재실행 N′ = 3.2e5 의 사전 등록 (v2)

- 작성: 2026-09-23 19:55 CDT 초안(v1) → 적대적 검토 2건(설계·통계 15건, 실행 가능성 13건; 워크플로 wf_82562c0d-220, 원문 `b32e4_review_raw/`) 반영 v2, Claude Code (Fable 5.1). 동결 시각 = 커밋 시각(아래 `DECISIONS.md` 줄). **결과 관측 전**: 이 예산의 어떤 체크포인트·적합도 BLER 로 평가된 적이 없다(적합·학습은 GPU 큐에서 진행 중, §0). 사용자 결정(2026-09-23 17:50~19:10 CDT): "더 큰 N_train 재실행", **N′ = 3.2e5**, **GMM K 격자는 b\* 가 내부가 될 때까지**. 커밋 뒤에는 §1~§3 의 규칙·임계값·예측을 바꾸지 않는다. 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 근거·틀: `10_SPEC_stageC.md` §6d(동일예산 곡선)·§6f(셀 일반화)·§5(D1 형제 게이트로 자격)·§3d(학습 발산 사다리)·A3(동일예산: GMM 도 같은 N′)·§6l(격자 확장), `01_RULES.md` §5(같은 데이터·같은 예산)·:76(**GMM arm 을 약화시키지 않는다 — K 전 범위 적합 + shrinkage + 검증 우도 early stopping**; "b\* 가 내부일 때까지 확장" 은 이 규칙의 §6l 해석), `08_SPEC_analysis.md` §2(판정점 3개 규칙, power guard, 앵커 = baseline arm), review_next v3 §0(테스트 집합 0..2559, 평가 가중치 = `_best.pt`, CPU 수신기, 결과 보존). 지금까지의 예산 곡선은 `docs/RESULTS.md` §1.
- 목적: **동일예산 우위(V1 < GMM b\*)가 예산 N′ = 3.2e5 에서도 유지되는가**, 그리고 예산 축 1e4 → 4e4 → 1.6e5 → 3.2e5 에서 격차가 어떻게 움직이는가(보고)를 답한다.
- 테스트 시행과 정보 상태(공개): 테스트 시행 0..2559 는 이전 세 예산·A1·P3 확증과 **같은 시행**이다(같은 채널·잡음 실현 → 예산 간 비교는 paired). N′ 의 어떤 선택(b\* = validation ll, 체크포인트 = val loss, 격자 확장 = ll_val)도 테스트 BLER 을 참조하지 않는다. 이 예산 점은 이전 예산의 테스트 결과를 **본 뒤** 추가됐다: 점별 판정은 독립된 사전 등록이지만 예산 축은 순차 선택이며(그래서 추세 검정은 등록하지 않는다), 이 결과를 보고 예산 점을 더 추가하려면 별도 등록이 필요하다. §3 의 예측은 이전 예산의 테스트 결과를 본 상태에서 적은 **약한 예측**이다.

---

## 0. 출발점 (판정에 쓰지 않는다)

| N_train | GMM b\* (Nr=8) | GMM BLER −3 dB | V1 BLER −3 dB | b\*→V1 pooled (3점) | D1 형제 게이트 |
|---|---|---|---|---|---|
| 1e4 | kron K=512 (내부) | 0.252 | 0.145 | 502:72, p=2.6e-80 | FAIL (GC 0.243) |
| 4e4 | kron K=2048 (격자 끝; K=1024 대비 +0.70 nat) | 0.248 | 0.145 | 459:79, p=3.9e-66 | FAIL (GC 0.167) |
| 1.6e5 | kron K=1024 (K=512 대비 +3.18 nat; **K=2048 미적합** — 격자 끝일 수 있음, 캐비엇으로 기록) | 0.243 | 0.145 | 454:78, p=1.7e-65 | PASS 레시피 (GC 0.0999) |

(C2, n=2560, 테스트 0..2559; `docs/RESULTS.md` §1.2~§1.3, §1.6.) V1 은 세 예산에서 0.145 로 같고, GMM 은 0.252 → 0.243 이다. 헤드라인 체크포인트는 last-EMA(best 미저장); H0(개발 집합)에서 best vs last 85:85. 공개: 지금까지의 GB′(`results/d2_gbprime.csv`) N=1.6e5 행은 모두 `gmm_ntrain=10000, equal_budget=False` — **동일예산 GB′ 는 아직 어느 예산에서도 계산된 적이 없고**, 이 문서의 GB′ 가 첫 동일예산 값이다(1.6e5 행과 직접 비교하지 않는다).

**이미 도는 것 (BLER 없음)**: `conf/code/run_b32e4.sh` (tmux `b32e4`, 2026-09-23 19:38 CDT 시작, 코드 4713b7ad) — GPU 큐 20 작업: kron K=2048·1024 재시작 0/1/2 (`fit_gpu.py 8 kron K 320000 B32e4 --restart r`), D2 score `run_d2_sx.py --ntrain 320000`(→ `ckpt/d2sx_N320000_a1.pt` + `_best.pt`; 끝의 GB′ 단계는 태그 라우팅이 없어 실패하고 rc ≠ 0 을 남기지만 체크포인트는 완성됨), D1 형제 `run_samplecx.py 320000`(→ `ckpt/sx_N320000_D1.pt` + 게이트), 나머지 격자 kron 512~16, full 512~16. 적합 프로토콜은 `runner.py fit` 과 동일(`fit_gpu.py`: kappa 격자, 재시작 3, 반복 상한 500, 검증 조기 종료, **선택은 validation log-likelihood 로만**). 실측 kron EM @3.2e5: K=1024 121 s/iter, K=2048 243 s/iter.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **예산** | N′ = 320000. 채널 집합 하나 = `arms.training_set("D2","S2",8,4,320000)` (= `train_rng(D2,S2,8,7)` 스트림의 앞 320000개). GMM 적합과 score 학습이 **같은 집합**을 쓴다(score 는 자체 9:1 분할, GMM 은 별도 검증 5000 = 스트림 8; 이전 예산과 동일, 10_SPEC A3). 가우시안 arm 의 Chat 도 같은 적합에서 온다 |
| **GMM 격자와 b\* (§6l 반복 규칙)** | 기본 격자 full K ∈ {16,…,512}, kron K ∈ {16,…,2048}. b\* = validation ll 최대(`arms.gmm_selection`). **반복 규칙**: b\* 가 어느 계열이든 그 계열의 최대 K 이면 2K 를 같은 프로토콜(재시작 3)로 적합해 다시 선택한다. **멈춤** = 그 계열 최대 K 의 ll_val ≤ K/2 의 ll_val (b\* 내부). 반복 상한 500 에 묶인 적합은 그대로 두고(상한을 늘리지 않음) §5 에 "상한 도달" 로 적는다. **K = 8192 가 필요해지면**(재시작당 ≈ 5일) 사용자 결정 뒤에만; 거부되면 b\* = K=4096(격자 끝)으로 실행하고 4e4 와 같은 "격자 끝" 캐비엇을 표 머리말과 §5 에 적는다. BLER 은 어디에도 쓰지 않는다. **선행 코드**: K=4096 적합을 시작하기 전에 `arms.D2_KS` 에 4096·8192 를 추가해 커밋한다(`load_fits` 는 존재하는 파일만 적재하므로 기존 태그 디렉터리의 선택은 바뀌지 않는다; 커밋 해시를 §5 에). 재시작 후보 파일이 누락되면 같은 시드의 그 재시작만 재실행(결정적)하고 §5 에 적는다 |
| **체크포인트·평가 가중치** | D2 `ckpt/d2sx_N320000_a1.pt`(last) 와 `ckpt/d2sx_N320000_a1_best.pt`(best, P0-1 코드). **판정에 쓰는 실행은 태그 `B32e4` = `_best.pt` 뿐**(v3 §0). last-EMA 실행(태그 `B32e4last`)은 예산 곡선 비교용 **보고 전용**이며 어떤 판정에도 쓰지 않는다(이전 세 예산은 모두 last-EMA). attempt 1 만(시드 반복은 등록하지 않음; 비용) |
| **학습 실패 처리 (§3d 그대로)** | D2 또는 D1 형제 학습이 `stopped_by=diverged` 또는 `aborted=True` 로 끝나면 10_SPEC §3d 사다리를 그대로 적용한다: 시행 2 = 기울기 클리핑 1.0, 시행 3 = 시행 2 + lr/3; 시행 간 선택은 val loss 만, 발산한 체크포인트로는 평가하지 않는다. 시행 3 도 실패하면 이 예산은 "학습 실패" 로 기록하고 BLER 을 돌리지 않는다. `stopped_by=max_epochs`(3000) 는 유효한 시행이며(01_RULES §5) 상한을 늘리지 않는다. **선행 코드**: `run_d2_sx.py`·`run_samplecx.py` 에 `--grad-clip`·`--lr-div` 인자(score.train 의 `grad_clip`, hp lr 조정)를 추가 — 시드 반복 미등록과 §3d 사다리는 별개다 |
| **자격 (D1 형제 게이트)** | `ckpt/sx_N320000_D1.pt`(**last 파일**, 1.6e5 선례와 같은 규약; `run_samplecx.py` 가 재는 파일) 의 GA~GD (임계 GA ≤ 1e-6, GB ≤ 0.05, GC ≤ 0.15, GD ≤ 0.20, 완화 없음; GA 는 구조적 0). `sx_N320000_D1_best.pt` 의 GA~GD 는 보고 전용이며 둘이 갈리면 last 가 자격을 정한다. 자격 한 행이 B32e4(best)·B32e4last(last) 두 실행에 같이 적용된다. **PASS → V0/V1/V4/V4b 는 arm 결과. FAIL → 이 예산의 학습 arm 결과는 §6d 규칙대로 "예산 축 측정"** 이고 표 머리말에 적는다. 어느 쪽이든 실행·보고한다. D2 체크포인트 자체에는 게이트 행이 없다("D1 형제 게이트 PASS 레시피" 로 쓴다, G-1.2) |
| **실행 (테스트 집합, 전 arm)** | 선행: `ln -s gmm_fits_D2_B32e4 results/gmm_fits_D2_B32e4x`, `…_B32e4last` (파일명에 n320000 이 있어 잘못된 링크는 fail-early). ① 판정: `runner.py run --testbed D2 --cell C2 --prior S2 --n 2560 --chunk 40 --ntrain 320000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N320000_a1_best.pt --tag B32e4` (7 SNR, 전 arm: R0~R5, gmm32, b\*, b\*-scalar, V0/V1/V4/V4b, genie). ② 보고 전용: 같은 명령을 `--cell C5 C1 --tag B32e4x` (§6f 셀 일반화, best). ③ 보고 전용: `--cell C2 --stagec-ckpt …/d2sx_N320000_a1.pt --tag B32e4last`. 수신기 CPU complex128, 16 반복, `arms.LOOP` 그대로. 그 뒤 `runner.py analysis --tag …`, `run_manifest.py --tag …`. **§5 가 채워져 커밋된 뒤에만 ①②③ 을 시작한다** |
| 수용 검사 | 각 태그: 점마다 raw 청크가 정확히 {(40k, 40): k=0..63}; raw meta `ntrain=320000`; `bstar`·`kron_K`·`ll_val\|kron` 이 §5 의 최종 선택·ll_val 과 일치; 세 태그의 `bstar`·`kron_K`·`em_sec` 동일, manifest 의 fits_dir 가 같은 디렉터리로 해석; `stagec_ckpt_id` 의 sha·epoch·best_epoch·role(best: B32e4/B32e4x, last: B32e4last)이 §5 와 일치; Demo 해시 동일. 어긋나면 그 실행 무효 → 원인 기록 후 새 태그로 재실행 |
| **판정 (셀 C2, 태그 B32e4, 기존 규칙 그대로)** | `08_SPEC` §2 표 B: `M-ours-bstar → M-ours-dscore-C-V1`, 판정점 3개 = 앵커 arm(b\*) 의 BLER@16 이 [0.005, 0.9] 안에서 **\|log10(BLER/0.1)\| 이 가장 작은** 3 SNR(`analysis.table_B` 가 자동 선택; 1.6e5 에서는 −3/0/+3 dB), 점마다 exact 양측 부호검정. **통과 = 출력 줄 기준: `power guard … -> POWERED` 이고 `second arm fewer failures at k/3 points` 의 k ≥ 2.** `significant` 토큰은 방향과 무관하게 찍히므로 판정 기준이 아니다(`first arm fewer failures at ≥2/3` 이면 GMM 우세로 "통과 못함"). 필수 대조군 `M-ours-bstar → M-ours-bstar-scalar` 도 같은 형식으로 보고(10_SPEC §3c) |
| 보고 전용 (판정 아님) | 예산 곡선 표(형식 고정): 행 = last-EMA 규약의 네 예산(1e4, 4e4, 1.6e5, **3.2e5 = B32e4last**), 열 = C2 −3 dB BLER(GMM b\*, V1), SNR@0.1 격차와 90% CI, pooled a:b; 3.2e5 의 `_best.pt`(B32e4) 값은 별도 열. **추세 검정은 등록하지 않는다**(4점, 순차 선택). C5·C1 표 B(앵커 규칙 자동), V0·V4·V4b, F3 가드 발동률, best 대 last 의 V1 짝 부호검정(C2), GB′(동일예산 b\* 기준, 첫 동일예산 GB′). **선행 코드**: `run_d2_sx.py` 에 `--tag`(→ `runner._init`) 를 추가해 `gmm_fits_D2_B32e4` 를 읽게 한다; csv 행은 `gmm_ntrain=320000, equal_budget=True, gmm_K = §5 최종 b*` 여야 한다 |
| **헤드라인 (여기서 고정)** | **헤드라인은 v3 §0 의 1.6e5(B16e4k)로 불변.** 3.2e5 는 예산 곡선의 한 점이며 이 문서 아래에서는 어떤 결과에서도 헤드라인 표를 대체하지 않는다. 원고에서 다른 예산을 헤드라인으로 쓰는 것은 결과를 본 뒤의 **사후 선택**이며, 하려면 `DECISIONS.md` 에 그렇게 명기한다 |
| 비용·일정 | GPU: kron 2048 ≈ 27~34 h/재시작(진행 중, 종료 ≈ 09-25 새벽 CDT), 1024 ≈ 14~17 h(종료 ≈ 09-24 10~13 CDT); D2 score ≈ 36~40 s/epoch × 1100~1450 epoch ≈ 12~16 h(max_epochs 3000 이면 ≤ 33 h), D1 형제 ≈ 2~3 h — 둘 다 K=1024 재시작이 GPU 를 비우는 뒤에 시작(큐 순서); K=4096 이 필요하면 ≈ 490 s/iter → 재시작당 2.5~3 일. CPU: 실행 ①②③ ≈ 각 30~60 분(192 워커) |

## 2. 판정·다음 단계 (여기서 고정)

| 게이트 (D1 형제, last) | 표 B `b\* → V1` (C2, B32e4) | 기록 |
|---|---|---|
| PASS | 통과 (POWERED, second arm fewer ≥ 2/3) | "동일예산 우위가 N′ = 3.2e5 에서도 유지" — arm 결과, 예산 곡선의 점. 헤드라인 불변 |
| PASS | 통과 못함 (그 밖의 전부: first arm fewer ≥ 2/3 포함, UNDECIDED 포함) | "N′ = 3.2e5 에서 우위 없음 / 판정 불가" 그대로 기록(출력 문자열 그대로). 헤드라인 불변, 예산 곡선 표에 실림; 원고의 범위 문장은 사용자가 다시 정한다 |
| FAIL | (어느 쪽이든) | "예산 축 측정" — 학습 arm 결과가 아님. 표는 싣되 arm 주장에 쓰지 않는다 |
| 학습 실패 (§3d 시행 3 까지) | — | BLER 미실행, "학습 실패" 로 기록 |

- 문장 범위: 통과해도 "학습 prior 가 GMM 보다 낫다" 를 셀·예산 한정 없이 쓰지 않는다(§6f). C5·C1 은 보고 전용이라 범위 문장을 바꾸지 않는다.
- P3 의 채택 규칙 R-adapt 는 이 문서에 넣지 않는다(헤드라인 표는 16 반복; R-adapt 표를 3.2e5 에서도 낼지는 별도 등록).
- 이 문서는 어떤 기존 판정(§6d·§6f·Stage C·review_next)도 바꾸지 않는다.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 이전 예산의 테스트 결과를 본 상태의 약한 예측)

1. D1 형제 게이트(last) **PASS**: GC ≈ 0.07 (GC ~ N^−0.474 외삽: 0.0999 × 2^−0.474 ≈ 0.072), GB·GD 도 통과.
2. GMM b\*: K=2048 이 K=1024 를 이겨 **격자 끝** → 규칙대로 K=4096 적합. 그 뒤 b\* = **2048(4096 이 지지 않음, 내부)** 또는 **4096(격자 끝 — K=8192 는 사용자 결정)**; K=4096 의 ll_val 이득은 +1 nat 미만.
3a. C2 판정(B32e4): **통과**(POWERED, second arm fewer ≥ 2/3). 3b. 세 판정점 **모두** 유의(3/3). 두 항목을 따로 채점한다.
4. C2 −3 dB BLER: **V1 ≈ 0.14~0.15 (예산에 무관)**, GMM b\* ≈ 0.235~0.245 (K 증가로 조금 개선); 격차(GMM − V1)는 1.6e5 의 0.098 보다 조금 줄어 0.09~0.10. pooled a:b 는 1.6e5(454:78) 와 같은 크기. 곡선은 "V1 평평, GMM 완만한 개선".
5. 대조군 `b\* → b\*-scalar`: GMM 쪽 우세(1.6e5 와 같은 방향). V0 의 F3 가드 발동률: 기록된 추세(0.712 → 0.702 → 0.529)를 따라 **0.529 이하** — §6d 의 "야코비안은 예산과 함께 나빠질 수 있다" 는 가정과 반대 방향의 예측이며 그 가정의 검정이다. V4·V4b 는 V1 보다 나쁨.
6. `_best.pt` 대 last-EMA 의 V1 차이(C2, 짝 부호검정): 판정 불가(H0 와 같음).
7. C5(B32e4x): 1.6e5 와 같이 판정점에서 혼재(1/3 유의). C1: GMM 우세(first arm fewer ≥ 2/3, 1.6e5 와 같음).
8. 빗나갈 경로: (a) 게이트 FAIL(GB 가 예산과 함께 나빠질 수 있음) → 예산 축 측정으로 기록; (b) GMM 이 V1 에 근접(격차 < 0.05) → "이득은 예산 효과" 로 기록(§6d); (c) K=4096 도 격자 끝 → K=8192 는 사용자 결정, 거부 시 격자 끝 캐비엇; (d) 학습 발산 → §3d 사다리.

## 4. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 |
|---|---|
| GPU 큐 `run_b32e4.sh` (kron 2048·1024 재시작, D2·D1 학습, 격자 나머지) | 진행 중 (19:38 CDT~) |
| 선행 코드: `arms.D2_KS` += 4096, 8192; `run_d2_sx.py` `--tag` + `--grad-clip`/`--lr-div`; `run_samplecx.py` `--grad-clip`/`--lr-div`; fits 링크 `gmm_fits_D2_B32e4x`·`_B32e4last` | **구현** (Opus, 2026-09-23 22:12 CDT). §3d 사다리 인자는 기존 관례(run_V3.py·run_d1_variant.py)대로 **`--fallback 2|3`** 한 인자로 구현(`score.GRAD_CLIP_LADDER`/`LR_DIV_LADDER` = 클리핑 1.0 / +lr/3, 같은 rung·attempt = 같은 데이터 스트림, 체크포인트 접미사 `_fb<k>`); `run_samplecx.py` 는 두 번째 위치 인자. 기본값(인자 없음)은 동작이 비트 동일(lr/1.0, grad_clip 미전달) — 큐의 7·8번 작업이 그대로 돈다. fits 링크 생성 |
| kron K=2048 / 1024 병합 (`fit_gpu.py 8 kron K 320000 B32e4 --merge`) → ll_val 비교 → 반복 규칙(K=4096 ?) | 대기 |
| `run_d2_sx.py --ntrain 320000 --tag B32e4` 재실행(GB′, 적합 완료 뒤; 학습은 완료 상태로 건너뜀) | 대기 |
| §5 채우기 → 커밋 → 실행 ①②③ + `analysis` + `run_manifest` | 미실행 |
| 예산 곡선 표 (`docs/RESULTS.md` §1 확장), EXPERIMENTS 행 | 미작성 |

예상 일정(CDT): K=1024 종료 09-24 10~13 → D2·D1 학습 시작 → D2 종료 09-25 새벽~오전; K=2048 종료 09-25 새벽; K=4096 이 필요하면 09-27~28; 그 뒤 §5·실행·기록.

## 5. 평가 전 고정 기록 (실행 ①②③ 전에 채우고 커밋한다; 갱신 시각을 적는다)

| 항목 | 값 (채워질 것) |
|---|---|
| 격자: K 별(계열별) 재시작별 ll_val · n_iter · it_best(상한 도달 여부), 병합 ll_val | [09-24 09:13 CDT] kron K=1024: r0 −10.621 (272 iter, best@270), r1 **−10.559** (341, best@300), r2 −10.941 (171, best@130); 상한 500 미도달; 병합 = r1, ll_val −10.559, ll_test −10.230, sec 합 93,569 (fit_gpu --merge, CPU). [09-24 11:19 CDT] kron K=2048: r1 −8.023 (231, best@190), r0·r2 진행 중. 나머지 K: 진행 중 |
| 확장 결정(K=4096 / 8192)과 시각, `arms.D2_KS` 변경 커밋 해시 | [09-24 11:19 CDT] **K=4096 적합 결정** — kron K=2048 재시작 1 이 ll_val −8.023 (231 iter, best@190, 55,742 s)으로 K=1024 병합 −10.559 보다 높다; K=2048 병합값은 재시작 최댓값이라 ≥ −8.023 이므로 b\* = kron 최대 K(2048) 가 확정 → §1 반복 규칙대로 kron K=4096 재시작 0/1/2 를 큐 맨 앞에 추가. `arms.D2_KS` 에 4096·8192 추가는 b212d683 (K=4096 적합 전). 반복당 ≈ 490 s(외삽) → 재시작당 ≈ 1.3~2 일 |
| 최종 b\*: 계열·K·ll_val, 내부 여부(또는 격자 끝 캐비엇) | |
| D2 체크포인트: last / best 의 sha256[:16]·epoch·best_epoch·stopped_by·aborted·init sha256[:16]·`torch.initial_seed`; best.epoch == last.best_epoch 확인 | |
| D1 형제: last 의 GA·GB·GC·GD 와 PASS/FAIL (best 는 보고 전용), stopped_by·aborted | [09-24 09:13 CDT] `sx_N320000_D1.pt` (last, epoch 200, best val @160): GA 9.52e-16, GB 0.00325, GC 0.0937, GD 0.0715 → **PASS** (`run_samplecx.py` → `samplecx.csv` 행 320000); stopped_by=patience, aborted=False, 200 epoch, 39.6 s/epoch. best 파일의 GA~GD 는 아직 재지 않음(보고 전용) |
| §3d 사다리 적용 여부(시행 번호) | |
| GB′ (동일예산, b\* 기준) worst excess | |
| 선행 코드 커밋 해시, fits 링크 생성 시각 | |
