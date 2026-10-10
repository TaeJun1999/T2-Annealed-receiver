# 적대적 검토 — NEXT_EXPERIMENTS_DMC16e4.md v1 (DeepMIMO 6 개 도시 28 GHz, prior DMC, 태그 DMCB16e4)

- 작성: 2026-10-10 18:07 CDT (= 10-11 08:07 KST), Fable 5.1, 적대적 검토 (A 설계·통계·문구 + B 실행 가능성·코드·사실, 한 보고서). 코드 기준 HEAD e44a9d8b (= 초안 커밋; `conf/code` 는 08a3e81d 와 동일, dirty 0). 읽은 것: 초안 v1 전체, `NEXT_EXPERIMENTS_38901.md` v2 §0~§6, `prereg_reviews_2026-09-26/review_{A,B}_PARETO_38901.md`, `code/{dmimo.py, dmimo_build.py, testbed_dm.py, run_dmc_gpu.sh, run_prior_eval.sh, run_tb2.sh, eval_accept.py, fit_gpu.py, fit_gpu_batched.py, run_d2_sx.py, sigma.py, em_batched_check_nr.py}` 전문, `common.py`(trial_rng·train_rng·make_gen·make_pilots·CELLS), `arms.py`(training_set·gmm_selection·fit_path·load_fits), `runner.py`(run_task 트라이얼 루프 :496–560, smoke :703, `_sets` :1034–1050, ckpt prior 검사 :1355–1375, 태그 요구 :1285–1290, learned_budget :272), `score.py`(training_split :653–665, train :835 머리말, gb_prime :1381–1436, `_rung_ix`), `analysis.py`(PAT :60, 배너 :667–680, decision_points :405–453), `recovery_ci.py`, `frontier_ci.py --recovery`, `guard_report.py`, `run_manifest.py` :60–135, 두 커밋의 diff(`git show 25f74c0a 08a3e81d`), `results/{testbed_DMC.txt, sigma_grid_D2_DMC.txt, nr8b_batched_check_DMC_n160000.txt}`, `logs/{train_d2sx_DMC_N160000_a1.log, sigma_DMC.log, tb2.log, tb2_queue.txt}`, `~/data/deepmimo/build_Nr8.log`, `testbed2_phase0/{report_deepmimo.md, selection.md}` + 6 개 도시 JSON, `docs/RESULTS.md` §10, `DECISIONS.md` [2026-10-11 07:51 KST], DeepMIMO 4.0.5 소스 `datasets/dataset.py`(compute_channels :464–534, `_compute_rotated_angles` :690–745, `_compute_single_array_response` :770–790), `generator/channel.py`(기본값 :160–175, OFDMPathGenerator.generate :357–428), `generator/geometry.py`(`_array_response`, `_ant_indices`, `_rotate_angles_batch`).
- 실행한 것 (모두 CPU, `CUDA_VISIBLE_DEVICES=`, `OMP_NUM_THREADS≤8`; 수신기·BLER 실행 없음, 저장소·`~/data` 쓰기 없음 — `find ~/data/deepmimo -newermt` 로 확인 0 파일): 스크래치 `/tmp/claude-1005/-home-HTJ-t2/b187bcb3-67a6-4fa2-86ce-8a8ed017508c/scratchpad/review_dmc/{rebuild_check.py, pool_check.py}`: ① `dmimo_build.build(8)` 을 `out_dir` 만 스크래치로 바꿔 **풀 세 번째 빌드** → sha·바이트 비교; ② DeepMIMO 경로 자료(power·phase·AoA/AoD + `_rotate_angles_batch`)로 **독립 조향 벡터 코드**로 300 쌍의 채널을 다시 만들어 `compute_channels` 와 비교; ③ `dmimo.calibrate` 로 P_RAW·TRAIN_SHA·Rt 재계산; 타일 키 충돌·풀 크기·비중·스트림→풀 대응·`_which` 거부 경로·테스트 풀 전체의 outage·도시별 비중; ④ `score._rung_ix`, 시드 배치, 중복 기대값; ⑤ `dm.load(max_paths=100)` 으로 시나리오 파일의 경로 상한 확인; ⑥ 기존 raw(`raw_U28B16e4`)의 meta 키 확인. 등급: **MUST**(없으면 동결·실행이 틀림) / **SHOULD** / **NIT**. 각 항목에 [실행 확인] 또는 [읽어서 추론] 을 적는다.

---

## 발견 (심각한 순)

### M1 · MUST · §3 예측 5·6·7 은 v2 동결 시각에 이미 관측된 값이 될 가능성이 크고, 초안은 동결과 격자 확정·GB′ 의 순서를 정하지 않았다 [실행 확인]

- 증거: 18:05 CDT 에 `logs/train_d2sx_DMC_N160000_a1.log` 는 epoch 183 (best 2.561612e-01 @183), 6.5 s/epoch → patience 정지는 빠르면 18:10 CDT 대, 느려도 수십 분 안. `logs/tb2_queue.txt` 는 18:05 CDT 에 **1 줄**(kron 4096 r2) 만 남았고 `gmm_fits_D2_DMCB16e4/` 에 15 파일(full 6 + kron 16..512 6 + kron 1024 후보 3) — 2048·4096 후보는 실행 중. 즉 v2 동결(검토 반영 뒤 커밋) 시각에는 학습 종료(epoch·stopped_by)·격자 파일 전부·`tb2_gpu*.log` 의 후보 ll_val 이 눈에 보인다. 초안 §4 의 행 순서는 "병합·격자 끝 규칙·GB′ (대기)" → "적대적 검토 → v2 → 동결 커밋 (대기)" 이고 §1 "실행" 은 "격자 확정·§5 채움·커밋 뒤에만" 이라 **동결이 병합·b\* 선택·GB′ 뒤에 와도 문서와 모순이 없다**. 그러면 §3-5 (GB′ median ≥ 0.9), §3-7 (b\* = kron 4096), §3-6 (epoch 200–600·patience) 은 관측 뒤에 채점되는 "예측" 이 된다. 38.901 v2 는 10:41 CDT 동결, 격자 확정 13:12, GB′ 14:36 으로 순서가 지켜졌다(38901 §5).
- 고침(두 군데, 문구 그대로):
  - §4 표에 행 하나 추가(둘째 행 뒤): `| **순서 규칙** | v2 동결 커밋 → kron 1024·2048 병합·b\* 선택 → (격자 끝이면 4096 병합) → GB′ 재개 → §5 채움·커밋 → 실행. 병합 파일(`fit_DMC_Nr8_kronK{1024,2048,4096}_n160000.npz`)·`d2_gbprime_DMC*.npz` 의 mtime 이 동결 커밋 시각보다 뒤여야 한다(§5 에 나란히 적는다) |`
  - §3 머리말 끝에 한 문장: `v2 동결 시각에 이미 관측된 항목은 예측이 아니라 관측이다: 동결 시각에 학습이 끝났으면 6 은 "관측됨 — epoch <n>, stopped_by <s> (채점 제외)" 로, 후보 ll_val 을 읽었으면 7 을 같은 식으로 바꿔 적는다. 1~4·8·9 는 BLER 이므로 그대로 예측이다.` — 후보 ll_val 은 `logs/tb2_gpu*.log` 에 찍히므로 v2 작성자는 그 로그를 읽지 않았음을 §3 에 적거나, 읽었으면 7 을 관측으로 돌린다.

### S1 · SHOULD · 두 arm 의 모델 선택은 모두 "학습 타일 안" 이고 테스트는 "다른 타일" 인데, 이 비대칭 없음/있음이 §1 에 명시되지 않았다; 또 `ll_test`·GB′ 는 테스트 풀 위의 수치다 [실행 확인]

- 증거: 스트림 8 → 검증 풀(20,000) 은 학습 풀과 **같은 459 타일**을 공유(`pool_check.py`: 학습 160000 의 타일 집합 ∩ 검증 5000 의 타일 집합 = 459/459, 테스트 타일과의 교집합 0). GMM 의 b\* 선택(`arms.gmm_selection`, ll_val 스트림 8)과 score 의 `_best`(`score.training_split` 의 9:1, 같은 160000 안)는 둘 다 타일 안 검증이고, BLER 은 다른 88 타일(TDMg: outage 0.217 vs 0.191, 도시 비중도 다름 — S3). 두 arm 에 같은 조건이므로 공정하지만, "검증 우도 최대" 가 테스트 쪽 성능 기준과 같지 않음은 DMC 에서만 생기는 성질이다. 또 `runner._sets` 의 (10, 5000) 과 `score.gb_prime` 의 스트림 10 은 **테스트 풀 복원 추출**이라 fit 파일의 `ll_test` 와 GB′ 는 테스트 모집단 위의 수치다(BLER 아님; 선택에 쓰지 않음).
- 고침: §1 "DMC 고유 사항" 에 (7) 추가: `(7) **선택은 타일 안, 평가는 타일 밖**: GMM 의 b\*(스트림 8, 검증 풀 = 학습 풀과 같은 459 타일의 다른 쌍)와 score 의 _best(160000 의 9:1 분할)는 둘 다 학습 타일 안의 검증으로 고르고, BLER 은 다른 88 타일에서 잰다 — 두 arm 에 같은 조건이며, 검증 우도 최대가 테스트 타일 기준과 같다고 가정하지 않는다. fit 파일의 ll_test(스트림 10, 5000) 와 GB′(스트림 10, 4096) 는 테스트 풀 위의 수치이고 선택·판정에 쓰지 않는다.`

### S2 · SHOULD · §3 예측 2 의 두 문장은 채점이 모호하다 [읽어서 추론]

- "ΔR 1차는 **포화 가드 또는** 'D2 보다 낮다'" 는 두 결과를 모두 적중으로 만든다(가드 발동 = 라벨 없음). "SNR@0.1 격차 < +0.60 dB" 는 격자 밖이면 "n/a" 가 나오는데 채점 규칙이 없다.
- 고침: `2. **크기는 UMi28 보다 작다**: SNR@0.1 격차(b\* − V1) 점추정 < +0.60 dB (어느 한쪽이 격자 밖 "n/a" 이면 채점 불가); 회수율 2차 R ≤ 0.15; ΔR 1차 90 % CI < 0 ("D2 보다 낮다"). 포화 가드가 발동하면 ΔR 항목은 채점 불가로 적는다(적중 아님).`

### S3 · SHOULD · "split 이동" 에 도시 비중 변화가 빠져 있다 — 테스트 풀은 학습 풀과 도시 구성이 다르다 [실행 확인]

- 증거(`pool_check.py`, 시나리오 순서 NY·MIA·LA·CHI·HOU·PHX): 학습 풀 비중 0.147/0.238/0.162/0.074/0.207/0.172, 검증 풀 0.147/0.239/0.157/0.072/0.209/0.176, **테스트 풀 0.115/0.251/0.165/0.083/0.165/0.220**. 88 타일의 추첨이라 도시별로 ±3–5 %p 어긋난다(NY −3.2, HOU −4.2, PHX +4.8 %p). LoS 0.282/0.277/0.278. 초안 (4)(5) 는 "쌍에 균등"·"통계가 조금 다르다(TDMg)" 만 적었다.
- 고침: (5) 를 `(5) **split 이동**: 테스트 타일은 다른 장소라 학습 쪽과 통계가 다르다 — TDMg(outage 0.217 vs 0.191) 에 더해 도시 비중이 학습 풀 NY/MIA/LA/CHI/HOU/PHX = 0.147/0.238/0.162/0.074/0.207/0.172 → 테스트 풀 0.115/0.251/0.165/0.083/0.165/0.220 (88 타일 추첨의 결과; 고치지 않는다).` 로.

### S4 · SHOULD · 누수 층화(보고 전용)의 정의에 재량이 남는 곳 세 군데 [읽어서 추론 + transmit 소비량 확인]

- 재현 가능성 자체는 문제없다: `runner.run_task` 의 시행 루프(:544–552) 는 `gen.sample(rng)`(DMGen 은 `rng.integers(0, 52172, 1)` 한 번) → `rng.integers(0, 2, K)` → `rng.permutation(Ns)` → `transmit`(`Demo/t2_route_a.py:287`: `rng.standard_normal((Nr, T))` 2 회) 뿐이라, 같은 순서로 소비하면 시행 t 의 쌍 색인이 그대로 나온다 (sigma.py 도 같은 루프). 그러나 (a) 층 안에서 b\* − genie ≤ 0 이면 R 이 정의되지 않는데 규칙이 없다; (b) 되찾은 쌍 색인으로 LoS·도시·BS 가 바로 나오므로 "계산하지 않는다" 를 스크립트 수준에서 못 박아야 한다; (c) 재생 스트림이 raw 와 맞는지 확인하는 검사가 없다(어긋나면 층이 엉뚱한 시행에 붙는다).
- 고침(보고 전용 칸의 누수 층화 문장 뒤에): `구현 규칙: `code/dmc_leak_strata.py` 는 run_task 의 루프(sample → integers(0,2,K) → permutation(Ns) → transmit 의 잡음 2 회)를 그대로 재생해 시행 t 의 쌍 색인을 얻고, d 만 계산한다 — 색인·meta 의 LoS/도시/BS 는 읽지 않는다(출력에 d 와 층만). 정렬 검사: 재생한 (H, u, perm, Y) 로 R5-genie 만 처음 40 시행 돌려 raw 의 `R5-genie|blk_err` 와 비트 동일해야 한다(본 실행 뒤, 보고 전용). 층에서 b\* − genie ≤ 0 이면 R = "n/a". 층별 n < 100 이면 R 을 적지 않고 실패 수만 적는다.`

### S5 · SHOULD · `~/data/deepmimo/build_Nr8.log` 가 찍은 split.npy sha 는 고정값과 다르다 — 빌드 출처 기록이 현재 코드와 맞지 않는다 [실행 확인]

- 증거: 로그 마지막 `POOL_SHA[8] = ('709a6346b0ea763b', '4d34bb25ffc99176')`; 디스크·`dmimo.POOL_SHA`·`testbed_DMC.txt` 는 `9f3237f1997d6b91`(`sha256sum` 확인). 커밋된 `dmimo_build.py` 로 스크래치에 세 번째 빌드(`rebuild_check.py`, 8 s): **H.npy·split.npy 둘 다 고정 sha 와 일치, 바이트 동일**(split dtype int8, 풀 270425/20000/52172). 즉 결정성은 성립하고 고정값은 맞지만, 로그는 split 부분이 달랐던 이전 코드의 산물이다. 초안 §1 "두 번 다시 빌드해 같은 sha" 는 로그로는 입증되지 않는다.
- 고침: §1 생성 모델 칸의 "두 번 다시 빌드해 같은 sha" 를 `두 번 다시 빌드해 같은 sha (빌드 로그 `build_Nr8.log` 의 split sha 4d34bb25ffc99176 은 커밋 전 코드의 것 — 검토 10-10 18:02 CDT 의 스크래치 재빌드가 고정값을 바이트 단위로 재현)` 로 바꾸거나, 커밋된 코드로 `~/data/deepmimo` 에 로그만 다시 찍어 둔다(풀 파일은 그대로; sha 가 같음을 확인).

### S6 · SHOULD · `run_prior_eval.sh` 의 머리말 prior 목록에 DMC 가 없다; 스크립트는 prior 를 검증하지 않으므로 실행은 되지만 §5 "인자 원문" 의 근거 문서가 어긋난다 [읽어서 추론]

- `run_prior_eval.sh:9` `prior  S2c | SV8e | UMi28 | MIX3`. 동작에는 영향 없음(`runner.py --prior` choices = `C.PID` 에 DMC 있음 — `common.py:105`). 동결 커밋에 주석 한 줄 추가: `prior  S2c | SV8e | UMi28 | MIX3 | DMC`.

### N1 · NIT · "P_RAW ≈ 1/512 = DeepMIMO 의 1/부반송파 수 **진폭** 인자" — 진폭 인자는 1/√512, 전력 인자가 1/512 [실행 확인]

- `channel.py:409` `a_pt = sqrt(power / total_subcarriers) · exp(…)`. 재계산 512·P_RAW = 1.00053. 고침: `(≈ 1/512: DeepMIMO 의 경로 진폭 √(p/N_sc), N_sc = 512 → 전력 1/512)`.

### N2 · NIT · §0 표 LoS 부분 −3 dB 격차 "0.290" → JSON `-3dB/LOS.lo_gap` = 0.28949 → **0.289** [실행 확인]. 나머지 표 값은 모두 일치(아래 "확인한 것").

### N3 · NIT · "num_paths 25" 의 뜻을 한 구절로 [실행 확인]

- `meta.npz`: 쌍의 45.7 % 가 경로 25 개(중앙값 22, 평균 17.1). `dm.load(max_paths=100)` 으로 다시 읽어도 사용자당 최대 25 → **시나리오 파일 자체의 상한**이며 잘라낸 경로는 없다; 25 개인 사용자의 경로는 전력 내림차순(확인 1.000). 고침: `num_paths 25 (= 시나리오 파일의 경로 상한; 쌍의 45.7 % 가 25 개, 버린 경로 없음)`.

### N4 · NIT · ν_q 덮음 문장(38901 §0 의 "C2 반복 1 의 ν_q = σ²/Tp …") 을 그대로 옮기면 좋다 [실행 확인]

- `sigma_grid_D2_DMC.txt`: C2 −3 dB it1 median 4.988e-01 = σ²/4; ν_hi 1.501 > 0.499 → 반복 1 질의는 격자 안. 문장: `C2 에서 반복 1 의 ν_q = σ²/Tp 는 결정적이므로 −3..15 dB 의 반복 1 질의는 격자 안에 있다(ν_hi 1.501 > σ²(−3 dB)/4 = 0.499).`

### N5 · NIT · `DMGen` 은 `.rot`(`--rotation`) 을 조용히 무시하고 `sample_paths`(`--doppler`) 가 없다 [읽어서 추론]

- `runner.py:508` `P["gen"].rot = …` 은 속성만 붙이고 DMGen 은 읽지 않는다; `--doppler` 는 AttributeError. 이 등록에는 둘 다 없으므로 영향 없음. 뒤에 DMC 로 ROT/DOP 류를 하려면 DMGen 에 `__setattr__` 가드(`rot` 금지) 를 넣는 새 커밋이 필요하다 — 지금은 §1 에 `DMC 는 --rotation/--doppler 를 지원하지 않는다(생성기가 무시/오류)` 한 구절이면 충분.

### N6 · NIT · §1 비용 "UMi28 실측 10:30–13:12 CDT" — `tb2.log` 의 UMi28 마지막 적합 종료는 12:27 CDT, 13:12 는 병합(수동) 시각 [실행 확인]. `격자 ≈ 2.7 h (UMi28 적합 09:4x–12:27 + 병합 13:12)` 정도로.

---

## 확인한 것 (직접 확인한 것만)

**풀·빌드·DeepMIMO (실행 확인)**
- 세 번째 빌드(커밋 코드, 스크래치)가 고정 sha `709a6346b0ea763b` / `9f3237f1997d6b91` 를 재현, H·split 바이트 동일; 풀 342597 = 270425 + 20000 + 52172, 타일 564 (88 테스트), 테스트 비중 0.1523.
- 독립 조향 벡터 재계산(300 쌍, 쌍별 yaw): `compute_channels` 대비 max rel diff 1.5e-07, |corr| 1.000000 → 채널 = Σ_l √(p_l/512) e^{jφ_l} a_UE(AoA 회전) a_BSᵀ(AoD 회전), y 축 ULA(`_ant_indices`), **쌍별 UE yaw 가 실제로 적용됨**(모든 사용자에 첫 사용자 yaw 를 쓰면 |corr| 0.33). `compute_channels` 출력 [user, rx=UE, tx=BS, k] → `transpose(0,2,1)` = 상반성(켤레 없는 전치) ✓, 단언 (8, 4) ✓.
- 경로 버림 없음: `generate` 는 delay_n ≥ 512 샘플을 0 으로 만들지만 기본 대역폭 10 MHz → 51.2 µs; 시나리오 최대 ToA 1.67 µs. 등방성이라 `_power_linear_ant_gain == power_linear` ✓. 부반송파 0 → 지연 위상 1 ✓. 쌍별 정규화 뒤 512·‖H‖²/(NrNt) 평균 1.018, min 0.146, max 2.66 (간섭; CV 0.396 과 부합).
- `los` ∈ {−1, 0, 1}(−1 = 경로 없음, 버림) ✓; yaw 범위 [−180, 180) ✓; 타일 키 충돌 없음(고유 (scen, tx, ty) 564 = 고유 key 564; 타일 좌표 −8..7 이라 100003 배수와 겹칠 수 없음).
- P_RAW 0.0019541542355243444 · TRAIN_SHA e6ddafc27367f975 · Rt 재계산 = 고정값(차 0).
- 스트림 → 풀: 7 → fit(160000 서로 다른 쌍), 8 → val(5000 서로 다른 쌍), 10·시행(C1 Tp2, C2, skip0 dev 포함) → test; EM 시드 배치(9)·D1 스트림 → ValueError. 학습 160000 의 타일 ∩ 테스트 타일 = ∅. 파이프라인이 채널을 뽑는 곳 전부(`arms.training_set` 7, `runner._sets` 7/8/10, `score.training_split`→training_set 7, `score.gb_prime` 10, `sigma.measure_point` 7+시행, `runner.run_task`/smoke 시행, `fit_gpu`/`em_batched_check_nr` → `_sets`) 가 허용 배치이므로 **중간에 ValueError 로 죽는 경로는 없다**(gates_D1 은 D1 전용, 호출 안 됨). 192 워커: 워커마다 `_pool` 한 번(88 MB sha + mmap + `np.where`), fancy indexing 은 복사 → 문제 없음.
- 복원 추출 중복 기대값 2560²/(2·52172) = 62.8 ✓(i.i.d. 시뮬 2497 distinct / 기대 2498.2); 테스트 풀 전체 outage −3 dB 0.192 (TDMg 0.1905 는 20000 표본).

**코드 경로 (읽어서 확인)**
- `run_prior_eval.sh DMC DMCB16e4 …` 가 부르는 전부에 DMC 경로가 있다: `runner.py run --prior DMC`(choices = C.PID; 비-S2 prior 는 `--tag` 필수 :1287; ckpt `prior` 일치 검사 :1362–1371), `analysis.PAT` 에 DMC(:60), `DM_WARNING` 배너·D2_WARNING 억제(:670–679), `table_D` DeepMIMO 분기(:530), `run_manifest.py` 채널 설명·코드 해시에 dmimo.py/dmimo_build.py, `eval_accept.py --prior DMC` 의 fit 파일 글롭 `fit_DMC_Nr8_<fam>K<K>_n160000.npz` = `arms.fit_path`, `recovery_ci`/`frontier_ci` 는 `analysis.load_raw`(PAT) 사용, `guard_report` 는 `D2_*.npz` 글롭. `fit_gpu.py … --merge --prior DMC` 인자 파싱·`_sets` 사용 ✓; `run_d2_sx.py --prior DMC` choices ✓, GB′ 재개 경로(`score.train(resume=True)` 무학습 → `A.gmm_selection` → `gb_prime` 스트림 10, sigma_tag 는 ckpt 에서) ✓, 산출 `d2_gbprime_DMC.csv`·`d2_gbprime_DMC_N160000_a1.npz` ✓. `learned_budget` 정규식 → `N_train=160000 rung=D2SXDMC160000` ✓(DECISIONS 의 DMC 작명 이유와 일치). `score._rung_ix("D2SXDMC160000")` = 1694 ✓ (UMi28 1665, MIX3 1276).
- 수용 검사 (a)~(e) 는 DMC 에서 모두 평가 가능: (b)(c)(d) 는 raw meta 키(`meta|ntrain·bstar·kron_K·ll_val|<b*>·em_sec·stagec_ckpt_id`, `raw_U28B16e4` 로 키 존재 확인)와 `--ref-raw raw_DMCB16e4` 재현; (a) 글롭; (e) 수동(mtime). 배너 검사는 템플릿과 같이 수동.
- 판정 규칙 = `analysis.decision_points`([0.005, 0.9] 안 |log10(BLER/0.1)| 최소 3 점, MIN_DISC 6, 앵커 = baseline) ✓; `recovery_ci.rec` 는 b\* − genie ≤ 0 → NaN(undefined) ✓; `frontier_ci.cmd_recovery` 는 undefined 복제 수를 찍음 ✓ — 초안 §1 의 포화 가드·정의 불가 규칙·(iv) 조건과 일치. b\* BLER@−3 이 [0.005, 0.9] 밖이면 판정점에서 빠지고 1차 ΔR 은 가드로 "범위 밖"; 3 점 미만이면 (iv) — 두 경우 모두 규칙이 닫혀 있다.
- GPU 큐 `run_dmc_gpu.sh` = 22 작업(@train 1 + kron1024 3 + full 6 + kron 6 + kron2048 3 + kron4096 3), UMi28 과 같은 순서 ✓; `run_tb2.sh train_chain` 의 ckpt 이름 `d2sx_DMC_N160000_a1[_fb<k>].pt` = §1 ✓.

**사실 대조 (파일 대 초안; 실행 확인)** — 모두 일치: testbed_DMC.txt 의 TDMa~TDMi 전 수치(1.00214/0.00281/0.396, 0.9960–1.0110, 342597/18/0.10°/0.281290, 0.3161 vs 0.3218, 3.422/25.27/0.872/0.854, 564/88/0.1523, 0.2819/0.2780/0.2170/0.1905/0.3161/0.3164/1.0017, 0.1261/0.433, 4 s), 날짜 07:39:20 KST @25f74c0a; σ 격자 20 점 ν_q [2.2391e-03, 1.5014e+00] → σ_t [3.3459e-02, 8.6642e-01], 헤드라인 대비 +1.2 %/+2.5 %; 일괄 EM 검사 (a)(b) 수치·재시드 2358/2358 @25f74c0a(em_batched_check_nr.py 의 choices 줄만 작업 트리); 학습 머리말 07:44:57 KST, split_hash 6fc8339a144a6d55, 479426 params, σ 격자 문자열, epoch 51 best 2.625866e-01, 22.9 → 6.5 s/epoch; 큐 시작 17:44 CDT (tb2.log); 빌드 시드 [20260926, 2, 12, 11], 시행 시드 [20260926, 2, 11, 8, 16, 4, snr+100]; zip sha 6 개; 0단계 JSON(격차 0.274/0.094, closed 0.56/0.68/0.71·0.52/0.63/0.66, LoS n 583/NLoS 1417, NLoS 0.267, closed LoS/NLoS 양쪽, LoS 0.281, 경로 중앙값 22·20 dB 안 4, 1/Σp² 1.72, erank 25.1, top-4 0.844, outage 0.236, 누수 0.411), report_deepmimo.md(105,842 / 130,969 / 342,597 쌍, closed 0.68/0.69/0.75–0.77, TwoNN 3.4/12.2, 학습 36000/검증 4000/테스트 2000), selection.md 8 행 "실패 (누수, outage)", RESULTS §10 의 UMi28 문맥(+3/+6/+9, 76:38·50:22·35:13, 161:73, +0.60 [+0.33, +0.87], R 0.062 [0.033, 0.089], ΔR −0.408 [−0.458, −0.358], kron 4096, GB′ 0.920) 과 D2 헤드라인 수치, DECISIONS [07:51 KST] 의 결정 (1)(2)(3) 문구.

**사용자 고정 사항 준수** — (1) DeepMIMO 만: Sionna RT 코드 호출 없음 ✓; (2) `dataset.compute_channels` 사용(`dmimo_build.py:80`) ✓; (3) C2 8×4·T16·Tp4·N′ 160000·검증 5000(`runner.N_VAL`)·7 SNR × 2560·chunk 40·동결 레시피 479,426·같은 K 격자 ✓; (4) UNGATED·헤드라인 불변 문구 ✓.

**문구 범위** — §2 라벨 문자열은 "DeepMIMO (6 개 도시 28 GHz, block split) 에서" 로 한정되고 :81 이 "ray-traced 채널에서"·"실측 채널에서" 를 금지 ✓; 머리말 "사이트 특정 ray-traced 채널(DeepMIMO)에서 … 잰다" 는 설명이지 주장이 아님. `DM_WARNING` 도 풀·split 을 명시.

**통계 공개** — 유한 풀·복원 추출(중복 ≈ 63)·쌍 균등 가중·yaw 고정·누수 0.433·outage 0.19 는 (1)~(6) 에 있고, 부호검정의 단위가 시행임을 적었다 ✓(S1·S3 의 보충만 남음). 다중성 "표 B 하나 + ΔR 1차 하나" ✓. 사후 분할 금지(LoS/도시/BS) ✓(S4 의 스크립트 수준 못 박기만).

---

## 판정

v1 은 **M1 을 고친 뒤 동결할 수 있다** — 동결 커밋을 병합·b\* 선택·GB′ 보다 앞에 두고, 동결 시각에 이미 보인 §3-5/6/7 은 "관측(채점 제외)" 로 바꿔 적는 것이 전부이며 §1·§2 의 규칙 자체는 38.901 v2 와 같고 DMC 에서도 닫혀 있다. S1~S6 은 공개·채점 명확화·출처 기록이라 v2 에 넣기를 권하지만 실행의 유효성을 바꾸지는 않는다. 코드 쪽은 추가 분기 없이 `run_prior_eval.sh DMC DMCB16e4 …` 가 `PRIOR_EVAL_DONE` 까지 갈 수 있고, 풀·보정 상수·채널 생성(쌍별 yaw·상반성·정규화·경로 버림 없음)은 독립 재계산으로 맞았다. v2 에서 다시 확인할 것: (가) 동결 커밋 시각 대 `logs/train_d2sx_DMC_N160000_a1.log` 의 종료 줄·`gmm_fits_D2_DMCB16e4/` 의 2048·4096 후보 mtime·`tb2_gpu*.log` 열람 여부를 §3·§4 에 그대로 적었는가; (나) `build_Nr8.log` 의 split sha 불일치를 §1 또는 §5 에 적었는가; (다) §5 의 9 인자 원문에 `"full:16,32,64,128,256,512 kron:16,…,<최종 K>"` 가 §1 격자 규칙대로 들어갔는가.
