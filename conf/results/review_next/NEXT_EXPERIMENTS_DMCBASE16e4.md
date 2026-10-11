# NEXT_EXPERIMENTS_DMCBASE16e4 — DeepMIMO (prior DMC, 셀 C2, N′ = 1.6e5) 에서 **등록된 baseline 전부**: PILOT16e4·ALD16e4·SPARSE16e4 의 절차를 DMC 한 행에 그대로 적용 (태그 PILDMC / ALDDMC / SPDMC) — 사전 등록 v2

- 작성: 2026-10-10 18:39 CDT (= 10-11 08:39 KST), Claude Code (Opus 5.5), 초안 v1 (커밋 2b88eb53) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-10/review_DMCBASE16e4.md`: MUST 1 · SHOULD 5 · NIT 7 — N1 을 뺀 전부 반영) → **v2 2026-10-10 19:02 CDT (= 10-11 09:02 KST)**. 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). 커밋 뒤에는 §1~§2 를 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 지시(2026-10-10 CDT, 이 세션): "Deepmimo로 다른 baseline들도 실험해야지. 우리 conference에 넣는 11개 그래프 모두 찍어야 해. 우선 하던거 마무리하고 진행하자".
- **작성 시점 공개**: DMC 의 수신기 BLER 은 **아직 한 번도 관측되지 않았다** — 주 실행 `DMCB16e4` (`NEXT_EXPERIMENTS_DMC16e4.md` v2, 동결 9d4c3b4a) 은 학습이 아직 돌고 있고(epoch 490) GB′·§5·실행이 남았다. 작성자가 본 DMC 의 것: testbed 통계(`results/testbed_DMC.txt`), 학습 곡선, GMM 격자와 b\* (kron 4096, ll_val 122.37953759128766; `logs/tb2_post_DMC.log`). 희소 baseline 조정(`sparse_tune.py --prior DMC --cell C2`, 개발 NMSE, BLER 없음)은 10-10 18:35 CDT 에 시작해 돌고 있고 아직 어떤 점수도 읽지 않았다. **이 v1 은 주 실행의 BLER 이 시작되기 전에 커밋한다**; 검토·v2 동결은 주 실행과 겹칠 수 있다(겹치면 동결 줄에 그때 무엇이 관측돼 있었는지 적는다). 이 문서의 실행은 주 실행이 끝나고 수용 검사를 통과한 뒤다.
- 목적: 원고 범례의 11 곡선(`conference/figures/paper_f16deep.py` `SHOW` = V1, ALD-pilot, b\*, R2-ours-G, R1-turbo, R3-bigamp, R0-pilot@1, SBL-loop, SBL-pilot, OMP-pilot, genie)을 DeepMIMO 에서도 모두 잰다. 주 실행(14 arm)이 일곱을 내고 **넷이 빠진다: ALD-pilot, SBL-loop, SBL-pilot, OMP-pilot**. `PIL` (V1-pilot, bstar-pilot) 은 11 곡선에 없지만 baseline 집합(𝔅 12 + 희소 3)을 다른 데이터셋과 같게 하려고 함께 돌린다(`pair_baselines.py`·`pair_ald.py` 가 그 raw 를 읽는다).
- 틀(새 규칙 없음): `NEXT_EXPERIMENTS_PILOT16e4.md` §1, `NEXT_EXPERIMENTS_ALD16e4.md` §1(조정 격자·끝 규칙·β 규칙·멈춤 단계·v 는 `code/ald.py` 에 고정), `NEXT_EXPERIMENTS_SPARSE16e4.md` §1(arm 정의·`per_snr_pick`·v2b 격자), `NEXT_EXPERIMENTS_STATIC16e4.md`·`NEXT_EXPERIMENTS_SUPP16e4.md` §1(표 B `X → V1`·라벨·X\*·R_X·가드, `pair_baselines --provenance manifest`). 다른 곳은 아래 "DMC 고유" 두 칸뿐이다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **시행·크기 (기존 실험과 같은 크기)** | 주 실행과 **같은 테스트 시행 0..2559** (prior DMC, PID 11 의 시행 스트림 → **주 실행 `raw_DMCB16e4` 와 시행 단위로 짝**), 셀 C2 (8×4, T 16, Tp 4), n = 2560, chunk 40, 7 SNR (−3..15 dB; 결과 뒤 늘리지 않는다), 16 반복, 수신기 CPU complex128. 가중치 = DMC16e4 §5 의 V1 `_best` 체크포인트(sha 는 §5), GMM = 주 실행의 b\* 적합(kron 4096; fits 링크 `gmm_fits_D2_{PILDMC,ALDDMC,SPDMC}` → `gmm_fits_D2_DMCB16e4`), N′ = 160000 |
| **arm 과 절차** | **PIL** (PILOT16e4 §1): `V1-pilot`, `bstar-pilot`, `R5-genie`, `runner.py run … --pilot-arms --tag PILDMC`. **ALD** (ALD16e4 §1): Arvinte–Tamir annealed Langevin 파일럿 추정(같은 V1 `_best` 가중치)을 GPU 로 사전 계산(`ald.py regen` → `tune`(개발) → `estimate`(테스트); 01_RULES §9.3 예외는 ALD16e4 와 같음), 수신기는 CPU: `ALD-pilot`, `ALDv-pilot`, `R5-genie`, `--ald-file results/ald/ald_PILDMC.npz --tag ALDDMC`; 조정은 `ald.py tune` 이 하는 그대로(c 격자 × β 격자, 끝이면 그 축 한 단계씩 최대 2 회 확장, β 규칙(개발 최적 β 가 저자 기본값 0.005 보다 0.1 dB 넘게 낫지 않으면 0.005 유지; `ald.py` `TIE_DB`), 멈춤 단계 = SNR 별 개발 평균 NMSE 최소, v = 그 단계의 개발 MSE/원소). **SPARSE** (SPARSE16e4 §1): `SBL-loop`, `SBL-pilot`, `OMP-pilot`, `R5-genie`, `--sparse-file results/sparse/pick_DMC_C2.json --tag SPDMC`; 하이퍼파라미터 = `sparse_tune.py --prior DMC --cell C2 --n 256` 의 `per_snr_pick` (v2b 격자 ρ {1,2,4,8,16}, n_em {1,2,3,5,10,25,50}, L {1,…,64}, L ≤ N), **격자 한 판으로 끝낸다 — 고른 값이 격자 끝이면 끝값 + 캐비엇, 더 확장하지 않는다**(SPARSE16e4 §1 의 C6 처리와 같음) |
| **DMC 고유 1 — 개발 채널은 테스트 풀에서 나온다** | ALD 의 개발 시행 = 시행 스트림의 2560..3071 (n = 512; 다른 데이터셋과 같은 정의) → DMC 에서는 테스트 풀 복원 추출. SPARSE 의 개발 채널 = 전용 스트림 `default_rng([20260930, TBID, PID, Nr, snr+100])`, n = 256/SNR → DMC 에서는 테스트 풀 복원 추출(`dmimo._which`, 커밋 ae880c27 — DMC16e4 동결 뒤·BLER 전의 추가이며 기존 스트림은 그대로). 둘 다 테스트 시행 0..2559 와 **다른 추첨**이지만 풀이 유한(52,172 쌍)이라 같은 쌍이 겹칠 수 있다 — 한 SNR 의 2560 테스트 시행이 덮는 쌍의 비율 1 − e^(−2560/52172) ≈ 0.048 → 개발 512 중 약 25 쌍, 256 중 약 12 쌍(채널은 같고 잡음은 다름). 다른 데이터셋에서 개발 채널이 테스트와 같은 생성기에서 나오는 것과 같은 처지이며 **baseline 에 유리한 방향**이다(조정량 c·β·멈춤 단계·v·ρ·n_em·L 모두 같은 방향); V1·b\* 의 학습·선택은 학습 타일 안에서만 한다(DMC16e4 §1 (7)). 조정 점수는 채널 추정 NMSE 뿐이다(BLER 없음) |
| **DMC 고유 2 — 앞선 라벨 기록이 없다** | 다른 데이터셋의 `run_sparse16e4.sh` 는 STATIC16e4 가 적은 𝔅 12 라벨을 `--expect` 로 기계 대조했다. DMC 에는 STATIC16e4 행이 없으므로 `--expect`·`--expect-bstar` 없이 한 번에 15 개를 모두 새로 계산한다 |
| **순서·열람 규칙** (검토 S3) | v2 동결 커밋 → (학습 정지 뒤) ALD 개발 재생성·조정 → 주 실행 수용 → §5 채움·커밋 → `run_dmc_base.sh`. **v2 동결 커밋은 다음을 읽기 전에 한다**: `results/sparse/{tune,pick}_DMC_C2.json` 과 `logs/sparse_tune_DMC_C2.log` 의 점수·pick, `results/ald/tune_PILDMC.json`, 그리고 `raw_DMCB16e4*`·`results/tables_D2_DMCB16e4*`·`results/review_next/{DMCB16e4_accept, recovery_DMCB16e4*}.txt`·`logs/{run_D2_DMCB16e4*, analysis_DMCB16e4*, run_prior_eval_DMCB16e4}.log` 의 어떤 BLER·라벨·실패 수. 동결 줄(`DECISIONS.md`)에 그때 무엇이 존재·열람됐는지 적는다. **동결 시각에 이미 관측된 항목은 예측이 아니라 관측이다**: pick 을 읽었으면 §2 2 의 L 문장을 "관측됨 (채점 제외)" 로, 주 실행 BLER 을 읽었으면 §2 1·3 을 "관측 뒤 작성 (채점 제외)" 로 바꿔 적는다. §1 의 "격자 한 판으로 끝낸다" 는 pick 을 읽기 전에 정한 것이다 |
| **실행** | **선행(수동, `~/t2/conf` 에서; 학습 정지(stopped_by 기록) 뒤)**: `CUDA_VISIBLE_DEVICES= python code/ald.py regen --tag PILDMC --prior DMC --cell C2 --fits-tag DMCB16e4 --set dev` (시행 2560..3071, CPU) → `CUDA_VISIBLE_DEVICES=<빈 GPU> python code/ald.py tune --tag PILDMC --ckpt ckpt/<stem>_best.pt` (**`--ckpt` 는 이 상대 경로 원문 그대로**: `ald.py estimate` 가 `a.ckpt == rec["ckpt"]` 와 ckpt_sha 를 assert 하고, 스크립트가 같은 문자열을 넘긴다) → `results/ald/tune_PILDMC.json` + `tune_PILDMC_curves.npz` 를 §5 와 같은 커밋에. **본 실행**: `code/run_dmc_base.sh <ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16>` (인자는 §5 가 기록한 값만). 전제(스크립트가 검사): 이 문서·`DECISIONS.md`·pick·tune JSON·`results/ald/tune_PILDMC.json` 이 git 추적 + clean, `conf/code`·`Demo` clean, 주 실행 `PRIOR_EVAL_DONE` 과 `DMCB16e4_accept.txt` = `ACCEPT: OK`, 체크포인트·pick·ALD 조정 기록의 sha = §5. 순서 **PIL → ALD → SP → pair_baselines**; 단계의 수용 검사가 실패하면 거기서 멈춘다(그 단계 무효, 원인 기록). 재개: 단계 출력 파일(accept·pair)은 그 단계가 통과했을 때만 생기며(실패 출력은 `.part`), 있으면 그 단계를 건너뛴다; `pairB_SPDMC.txt` 가 있으면 중단(재실행은 사용자 승인) (검토 M1·N2). GPU 는 ALD 추정에만 한 장(빈 GPU 가 없으면 멈춤, 재시도 없음). 로그 `logs/run_dmc_base.log`, 끝 표시 `DMC_BASE_DONE`. **실행 중 main 커밋 금지**(raw 의 `run\|git` 은 한 커밋; `pair_baselines --provenance manifest` 를 넘기지만 DMC 의 raw 는 모두 `run\|git` 을 가지므로 실제 적용 규칙은 "한 개의 깨끗한 커밋" 이다) |
| **수용 검사** | 태그마다 `eval_accept.py` (청크 {(40k, 40): k = 0..63} × 7 SNR, meta `ntrain`·`bstar`·`kron_K`·`ll_val`, 체크포인트 sha·role(PIL·ALD), 16 반복, **R5-genie 가 `raw_DMCB16e4` 와 7 SNR 전 시행 비트 동일**); PIL: `pair_cross.py` 무결성; ALD: `pair_ald.py` 무결성(추정 파일·시행 정렬); SP: pick 이 `per_snr_pick` 으로 재현되고 tune JSON 이 prior DMC·cell C2·n 256·v2b 격자, 메모리 가드, 모든 청크의 `meta\|sparse` = 그 SNR 의 pick |
| **판정** | `pair_baselines.py --base raw_DMCB16e4 --pil raw_PILDMC --ald raw_ALDDMC --est PILDMC --extra raw_SPDMC --add-baselines SBL-loop SBL-pilot OMP-pilot --cell C2 --prior DMC --r0 at1 --provenance manifest` → 표 B `X → V1`, X ∈ 𝔅 15 = {M-ours-bstar-scalar, M-ours-gmm32, R0-pilot@1, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, bstar-pilot, V1-pilot, ALD-pilot, ALDv-pilot, SBL-loop, SBL-pilot, OMP-pilot} → **새 라벨 15 개**. 라벨·판정점(앵커 = X, BLER@16 이 [0.005, 0.9] 안에서 0.1 에 가장 가까운 3 SNR)·power guard·X\*·R_X·가드는 SUPP16e4 §1 그대로: (i) = POWERED 이고 V1 이 ≥ 2/3 점에서 적게 실패(판정점마다 정확 양측 부호검정 p < 0.05; 판정점 = \|log10(BLER/0.1)\| 최소 3 SNR), (ii) = X 가 ≥ 2/3, (iii) = 방향 없음, (iv) = 검정력 미달. `b* → V1` 은 DMC16e4 §6 의 라벨을 인용한다(같은 raw 에서 `pair_baselines` 가 다시 낸 값이 다르면 드리프트로 적는다). 출력 `results/review_next/pairB_SPDMC.txt` |
| **"전부" 문장** | DMC16e4 의 `b* → V1` 이 (i) **이고** 15 개가 모두 (i) ((ii) 0) → "DeepMIMO (6 개 도시 28 GHz, block split) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"; 여기에 **R_{X\*}(−3 dB) 90 % CI 하한 > 0** (X\* = 16 개 중 −3 dB 실패 최소, 동률 이름순; `pair_baselines` 의 "'등록된 baseline 전부와 멀어진다' condition … MET" 줄) 이면 SPARSE16e4 §1 과 같은 문장 "등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다" 를 쓴다 — 포화 가드·genie ≥ V1 가드로 R_{X\*} 가 정의되지 않으면 "멀어진다" 문장은 쓰지 않는다(DMC16e4 §3 예측 4 "genie 가 높다" 가 맞으면 이 경우가 흔할 수 있다; 결과와 무관하게 미리 적음). 아니면 (i) 의 수와 (i) 가 아닌 arm 의 이름·라벨을 그대로 적고 "전부" 를 쓰지 않는다. (ii)(iii)(iv) 에서 "비긴다"·"동등" 문구를 만들지 않는다. 모든 문장에 DMC16e4 §1 "DMC 고유 사항" (1)(2)(3)(유한 풀·누수 0.433·outage)과 위 "DMC 고유 1" 을 붙인다. 범위: 이 풀·이 split·이 크기 한정 |
| **다중성** | 새 라벨 15 개 + 인용 1 개; 등록 사이 보정 없음(다른 데이터셋과 같은 관례 — 원고에서 등록 검정 수를 밝힌다) |
| **그림** | DMC 의 11 곡선은 전 SNR n = 2560 으로 그린다. 다른 데이터셋의 고 SNR 보강(FIGHS16e4, +6..+15 dB n = 20480)은 DMC 에 하지 않는다 — 하려면 별도 등록 |
| 보고 전용 | ALD 조정 표(`results/ald/tune_PILDMC.json`: c, β, 멈춤 단계, v, 개발 NMSE), SPARSE 조정 표·끝값 여부, raised trials 수, `pair_cross`·`pair_ald` 의 등록 비교(다른 데이터셋과 같은 형식; 새 라벨로 세지 않는다). 누수 층화는 주 실행(b\*·V1·genie)에만 있고 baseline 으로 넓히지 않는다 |
| 비용 [추정] | SPARSE 조정 CPU 2 스레드 ≈ 3.3 h (UMi28 실측 11,872 s); ALD 조정·추정 GPU 한 장 ≈ 10 분; PIL ≈ 10 분·ALD ≈ 5 분·SP ≈ 30 분(CPU 192 워커; 6 데이터셋 실측 38 분·11 분·78 분에서) |

## 2. 미리 적는 예측 (빗나가면 그대로 쓴다; DMC 의 BLER 은 본 적이 없다)

1. 15 개 가운데 **(ii) 0 이고 (i) ≥ 13 → 적중**; 둘 중 하나라도 아니면 빗나감((iv) 는 (i) 에 세지 않는다). 확신 중간(선례: D2 C2·D3·UMi28·MIX3 에서 15/15 (i); SV8e 에서 4 개(bstar-scalar·gmm32·V1-pilot 포함), C6 에서 V1-pilot 이 (iv)). (i) 가 아닐 후보는 `V1-pilot`·`bstar-pilot` (루프의 이득이 작을 때).
2. 조정 결과(채점 = `pick_DMC_C2.json`): OMP 의 L 이 −3·0 dB 에서 ≤ 4 (유효 경로 수 중앙값 1.7). BLER(채점 = `pairB_SPDMC.txt` 의 "BLER@16 failures / n per SNR" 표, 수치 비교·검정 없음): −3·0 dB 모두 `OMP-pilot` < `R0-pilot@1` 이고 `SBL-pilot` < `R0-pilot@1`.
3. 같은 표에서 −3·0·+3 dB 모두 `ALD-pilot` > `V1-pilot` 실패 수; 그리고 `pair_ALDDMC.txt` 의 A3 (`ALDv-pilot → V1-pilot`) = (i).
4. 빗나갈 경로: (ii) 가 하나라도 나오면 그대로 적는다 — 조정을 다시 하지 않고, 격자를 늘리지 않고, 사후 설명은 사용자.

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 |
|---|---|
| `dmimo._which` 에 sparse_tune 개발 스트림 → 테스트 풀, `run_dmc_sparse_tune.sh` | 완료·커밋 ae880c27 |
| SPARSE 조정 (tmux `sptdmc`, CPU 2 스레드) | 완료: 10-10 18:35 → 21:28 CDT (`SPARSE_TUNE_DONE rc=0`) → `results/sparse/{tune,pick}_DMC_C2.json` (§5) |
| `run_dmc_base.sh` (세 스크립트의 행 본문을 DMC 한 행으로) | 커밋 2b88eb53, 검토 반영(M1·N2·N6) = v2 동결 커밋 |
| ALD 개발 사이트 재생성·조정 (`ald.py regen --set dev`, `ald.py tune`; GPU 한 장) | 완료: 10-10 19:17 → 19:26 CDT (`code/run_dmc_post_gpu.sh`, GPU 1; 학습 정지 19:17 CDT 뒤) → `results/ald/tune_PILDMC.json` (§5) |
| 적대적 검토(Fable) → v2 → 동결 커밋 | 검토 끝(10-10 18:55 CDT 보고; MUST 1 · SHOULD 5 · NIT 7). 반영: M1 재개 키(`out` 헬퍼; 통과한 단계만 제 이름), S1 "멀어진다" 조건, S2 β 규칙 0.1 dB, S3 순서·열람 규칙, S4 ALD 조정 명령 원문, S5 예측 채점, N2 pairB 덮어쓰기 금지, N3·N4·N5·N7 문구, N6 b\* 상수 사전 검사. 반영하지 않은 것: N1 (`CUDA_DEVICE_ORDER`; 원본 `run_ald16e4.sh` 와 같게 둔다 — 동일 GPU 6 장, Exclusive_Process 라 어긋나면 오류로 멈춘다). **동결 시점(2026-10-10 19:02 CDT)의 관측 상태**: DMC 의 BLER 없음(주 실행 미시작; 학습 epoch 696, `tb2_train_state_DMC.txt` = none); `results/sparse/{tune,pick}_DMC_C2.json` 아직 없음(조정 진행 중; 로그의 점수·pick 을 읽지 않았다 — 읽은 것은 프로세스 생존과 줄 수뿐); `results/ald/tune_PILDMC.json` 없음(조정 전) |
| 주 실행 DMCB16e4 `PRIOR_EVAL_DONE`·ACCEPT OK → §5 → `run_dmc_base.sh` → §6 → 기록 감사(Fable) | 주 실행 10-10 20:04 → 21:53 CDT `PRIOR_EVAL_DONE`, `ACCEPT: OK -- DMCB16e4, DMCB16e4last`; §5 채움(10-10 21:53 CDT; 커밋 3ddb0831 21:55 CDT) → 이 커밋 뒤 `run_dmc_base.sh` |
| 실행 (갱신 10-10 22:22 CDT) | `run_dmc_base.sh` 10-10 21:55 CDT 시작(git 3ddb0831) → PIL 통과(21:57 CDT `ACCEPT: OK -- PILDMC`) → ALD 단계에서 `ABORT: no free GPU for the ALD estimate` (GPU 6 장이 컨테이너 밖 프로세스로 점유; 등록된 동작). 사용자 지시 "GPU 다 우리거니까 지금은, 계속 진행해" 뒤 GPU 5 에 컨텍스트 한 번 시도 → `cudaErrorDevicesUnavailable`. **편차(수치 불변; `DECISIONS.md` 같은 시각 줄)**: ALD 를 미루고 SP 를 먼저 — `DEFER_ALD=1 bash code/run_dmc_base.sh <§5 인자>` (옵트인 스위치, 기본 동작 불변) → SP 뒤 `DMC_BASE_PARTIAL`; GPU 가 비면 같은 스크립트로 ALD → `pair_baselines` |
| SP 단계 (갱신 10-10 22:30 CDT) | 10-10 22:22 CDT 시작(git 5aa7b9b4, `ALD deferred`) → runner 5.6 분 → 22:28 CDT `ACCEPT: OK -- SPDMC` (pick 규칙 재현, `meta\|sparse` 불일치 0, raised 0 / 0 / 0) → `DMC_BASE_PARTIAL`. 남은 것: ALD 단계(GPU 한 장) → `pair_baselines` |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다)

갱신 2026-10-10 21:53 CDT (Opus 5.5). 값은 파일에서 읽었다(`results/sparse/pick_DMC_C2.json`·`tune_DMC_C2.json`, `results/ald/tune_PILDMC.json`, `sha256sum`, 파일 mtime).

| 항목 | 값 |
|---|---|
| 체크포인트 (DMC16e4 §5 와 같음) | stem `d2sx_DMC_N160000_a1`, best `ckpt/d2sx_DMC_N160000_a1_best.pt` sha256[:16] **65b26ddd4f6437f4** (epoch 812). GMM = 주 실행의 b\* kron K = 4096, ll_val 122.37953759128766 |
| SPARSE 조정 (`sparse_tune.py --prior DMC --cell C2 --n 256`, tmux `sptdmc`, CPU 2 스레드) | 10-10 18:35 → 21:28 CDT (`logs/sparse_tune.log` `SPARSE_TUNE_DONE rc=0`; wall_sec 10367.1), 시작 커밋 ae880c27. `results/sparse/pick_DMC_C2.json` sha256[:16] **ff25622dfcb0c7d5**, `tune_DMC_C2.json` **a16ae2aad0db242d** (둘 다 mtime 10-10 21:28:44 CDT — v2 동결 19:02 CDT 뒤; 주 실행 BLER(20:04–21:52 CDT)과 겹쳐 돌았다 — 조정 점수는 개발 채널 추정 NMSE 뿐이고 BLER 을 읽지 않는다) |
| SPARSE 고른 값 (`per_snr_pick`, v2b 격자) | **SBL**: ρ = 8 (끝값 아님; 점수 −15.408 dB), n_em −3 dB 3 · 0…15 dB 5 (끝값 없음), 개발 NMSE −7.08 / −9.77 / −12.67 / −15.33 / −17.94 / −21.11 / −23.96 dB. **OMP**: **ρ = 16 = 격자 끝(`edge_rho_omp` true) → 끝값 + 캐비엇, §1 대로 확장하지 않는다**(점수 −14.202 dB), L −3…15 dB = 2 / 2 / 3 / 4 / 6 / 8 / 12 (끝값 없음), 개발 NMSE −7.74 / −9.93 / −11.87 / −13.87 / −15.97 / −18.77 / −21.26 dB |
| ALD 조정 (`ald.py regen --set dev` → `ald.py tune --tag PILDMC --ckpt ckpt/d2sx_DMC_N160000_a1_best.pt`; `code/run_dmc_post_gpu.sh`, GPU 1) | `results/ald/tune_PILDMC.json` sha256[:16] **8c92ea491d654012** (mtime 10-10 19:26:40 CDT, git 48803fe6, ckpt_sha 65b26ddd4f6437f4, `ald_py_sha` 5d38e28679cc7542, n_dev 512, dev_skip 2560), `tune_PILDMC_curves.npz` 5a8c367b695c979f. 고른 값: **c = 0.01, β = 0.005** — 개발 최적은 c = 0.01, β = 0.0001 (−16.180 dB)이나 저자 기본값 β = 0.005 가 0.1 dB 안(−16.171 dB)이라 규칙대로 유지; β 축을 0.0001·1e-05 로 두 번 확장, 확장 뒤 끝값 없음(`optimum_at_edge_after_extension` 빈 목록). 멈춤 단계 −3…15 dB = 384 / 453 / 504 / 598 / 600 / 600 / 600 (L 200 × M 3 = 600 이 상한), v = 0.1332 / 0.0662 / 0.0362 / 0.0190 / 0.0104 / 0.0056 / 0.0035, 개발 NMSE −8.06 / −11.02 / −13.52 / −16.46 / −18.94 / −21.44 / −23.75 dB |
| 주 실행 전제 | `logs/run_prior_eval_DMCB16e4.log` `PRIOR_EVAL_DONE`, `results/review_next/DMCB16e4_accept.txt` 첫 줄 `ACCEPT: OK` (스크립트가 검사; 이 커밋 시점에 충족 — DMC16e4 §6) |
| §2 예측 가운데 BLER 전에 채점되는 것 | 2 의 앞 문장(OMP 의 L 이 −3·0 dB 에서 ≤ 4): **적중** (2 / 2). 나머지는 실행 뒤 |
| **v2 동결 뒤·이 실행 전에 관측한 것(공개)** | 주 실행 `DMCB16e4` 의 BLER·표 B(14 arm; 11 곡선 가운데 일곱)를 이 §5 를 쓰기 전에 읽었다 — §1·§2 는 그 전에 동결됐고(501e0635) 이 §5 의 값은 모두 동결된 절차가 정한 것이다(조정 규칙·격자·끝 처리 불변, 재조정 없음) |
| 스크립트 인자 원문 | `bash code/run_dmc_base.sh d2sx_DMC_N160000_a1 65b26ddd4f6437f4 ff25622dfcb0c7d5 8c92ea491d654012` (tmux; ALD 추정에 빈 GPU 한 장) |

## 6. 결과 (2026-10-10 21:55~22:48 CDT, `run_dmc_base.sh` 세 번 시작; 이 절은 추가만 한다; 전사 커밋 3e91b94b (10-10 22:53 CDT); 기록 2026-10-10 22:51 CDT, Opus 5.5 — 전사만, 해석 없음)

수치의 출처: `results/review_next/pairB_SPDMC.txt` (표·요약 줄을 정규식으로 읽어 옮김), `pair_PILDMC.txt`, `pair_ALDDMC.txt`, `{PILDMC,ALDDMC,SPDMC}_accept.txt`, `logs/run_dmc_base.log`, `logs/run_D2_{PILDMC,ALDDMC,SPDMC}.log`.

**실행·운영 기록 (등록 대비 편차 포함; 수치 불변)**
- **시작 1** 10-10 21:55 CDT (git 3ddb0831 = §5 커밋): PIL runner 2.2 분 → 21:57 CDT `ACCEPT: OK -- PILDMC`, `pair_cross` 무결성 OK(raised 0 / 0) → ALD 시험 사이트 재생성(CPU) → `ABORT: no free GPU for the ALD estimate` (등록된 동작). GPU 6 장은 21:55 CDT 직전부터 이 컨테이너 밖 프로세스가 점유(장당 39,689 MiB, Exclusive_Process).
- **편차 1 — 단계 순서**(`DECISIONS.md` 10-11 12:22 KST 줄; 사용자 "GPU 다 우리거니까 지금은, 계속 진행해" · "그러네. GPU 안쓰는거 먼저 해보자"): 사용자 지시 뒤 GPU 5 에 CUDA 컨텍스트를 한 번 시도 → `cudaErrorDevicesUnavailable` (재시도 없음). 등록 순서 PIL → ALD → SP 대신 **PIL → SP → ALD**. 구현 = `run_dmc_base.sh` 의 옵트인 스위치 `DEFER_ALD=1` (커밋 5aa7b9b4; 기본 동작은 등록 그대로; `git diff 3ddb0831 ff736ea2 -- conf/code Demo` = 이 스크립트 한 파일 +10 −2 줄). 단계는 서로의 출력을 읽지 않는다.
- **시작 2** 10-10 22:22 CDT (git 5aa7b9b4, `DEFER_ALD=1`): `ALD deferred` → pick 규칙 재현(`rule-reproduced=True`, 메모리 필요 ≈ 264 GB / 가용 1021 GB) → SP runner 5.6 분 → `meta|sparse` 불일치 0, raised 0 / 0 / 0 → 22:28 CDT `ACCEPT: OK -- SPDMC` → `DMC_BASE_PARTIAL`.
- **시작 3** 10-10 22:46 CDT (git ff736ea2; GPU 0·1·2 가 빈 것을 `nvidia-smi` 로 확인한 뒤, 스위치 없이 — 확인은 로그 외 사실; ALD 시험 사이트 파일 `pilots_PILDMC_test.npz` 는 시작 1 의 것(21:57 CDT)을 재사용): ALD 추정 GPU 0 (22:47 CDT; `results/ald/ald_PILDMC.npz` sha256[:16] ddee100645e9d8ab) → ALD runner 0.4 분 → `ACCEPT: OK -- ALDDMC`, `pair_ald` 무결성 OK(raised ALD 시행 없음) → `pair_baselines` rc 0 → 22:48 CDT `DMC_BASE_DONE rc=0`.
- **편차 2 — 단계 사이 커밋**: 5aa7b9b4 (22:22 CDT, 시작 2 직전)와 ff736ea2 (22:31 CDT, 시작 2 종료 뒤·시작 3 전)는 runner 가 돌지 않을 때 했다. raw 마다 깨끗한 커밋 하나: `pair_baselines` 머리말 `git base=27737b62 extra0=5aa7b9b4 pil=3ddb0831 ald=ff736ea2; integrity: OK`.
- **편차 3 — 부분 결과 열람**: ALD 단계 전에 `pair_PILDMC.txt` 와 raw 에서 읽은 10 곡선의 실패 수(미리보기 그림 포함)를 봤다. §5 뒤라 조정값·규칙·명령은 이미 고정돼 있었고 바꾼 것이 없다.
- 비용: §1 추정 PIL ≈ 10 분 · ALD ≈ 5 분 · SP ≈ 30 분 → runner 실측 2.2 · 0.4 · 5.6 분.

### 6.1 표 B `X → V1` — 새 라벨 15 개 + 인용 1 개 (C2, prior DMC, UNGATED; 앵커 = X, R0-pilot 은 @1)

| X | 판정점 [dB] | a:b (X 만 실패 : V1 만 실패) | pooled (p) | 가드 · 유의 점 수 | 라벨 | F_X − F_V1 (−3 dB) | R_X (−3 dB) [90 %] | R_X (판정점 합) [90 %] |
|---|---|---|---|---|---|---|---|---|
| b\* (DMC16e4 인용) | +9 / +12 / +15 | 127:46 · 111:42 · 119:36 | 357:124 (3.4e-27) | POWERED, V1 3/3 · X 0/3 | **(i)** | 96 | 0.202 [0.166, 0.240] | 0.279 [0.241, 0.316] |
| b\*-scalar | +9 / +12 / +15 | 130:52 · 113:45 · 119:33 | 362:130 (2.4e-26) | POWERED, V1 3/3 · X 0/3 | **(i)** | 113 | 0.229 [0.193, 0.267] | 0.278 [0.241, 0.315] |
| gmm32 | +9 / +12 / +15 | 221:38 · 185:31 · 209:37 | 615:106 (4.9e-88) | POWERED, V1 3/3 · X 0/3 | **(i)** | 134 | 0.261 [0.222, 0.299] | 0.458 [0.428, 0.489] |
| R0-pilot@1 | +9 / +12 / +15 | 772:1 · 754:1 · 789:0 | 2315:2 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 391 | 정의 안 됨 (범위 밖: 0.9871) | 0.793 [0.780, 0.807] |
| R1-turbo | +9 / +12 / +15 | 406:16 · 362:21 · 374:17 | 1142:54 (4e-266) | POWERED, V1 3/3 · X 0/3 | **(i)** | 315 | 정의 안 됨 (범위 밖: 0.9574) | 0.643 [0.621, 0.667] |
| R2-ours-G | +9 / +12 / +15 | 325:27 · 279:22 · 310:21 | 914:70 (2.9e-188) | POWERED, V1 3/3 · X 0/3 | **(i)** | 194 | 정의 안 됨 (범위 밖: 0.9102) | 0.583 [0.558, 0.610] |
| R3-bigamp | +6 / +9 / +12 | 638:6 · 791:4 · 960:2 | 2389:12 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 325 | 정의 안 됨 (범위 밖: 0.9613) | 0.786 [0.773, 0.800] |
| R4-llr | +9 / +12 / +15 | 1044:2 · 1076:3 · 1149:5 | 3269:10 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 387 | 정의 안 됨 (범위 밖: 0.9855) | 0.844 [0.833, 0.854] |
| R4-scvamp | +9 / +12 / +15 | 682:4 · 708:4 · 756:3 | 2146:11 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 341 | 정의 안 됨 (범위 밖: 0.9676) | 0.780 [0.765, 0.795] |
| bstar-pilot | +9 / +12 / +15 | 147:52 · 129:41 · 131:29 | 407:122 (7.8e-37) | POWERED, V1 3/3 · X 0/3 | **(i)** | 187 | 정의 안 됨 (범위 밖: 0.9074) | 0.321 [0.285, 0.356] |
| V1-pilot | +9 / +12 / +15 | 35:25 · 21:9 · 14:8 | 70:42 (0.01) | POWERED, V1 1/3 · X 0/3 | **(iii)** | 120 | 0.240 [0.204, 0.277] | 0.044 [0.015, 0.072] |
| ALD-pilot | +9 / +12 / +15 | 123:43 · 150:37 · 208:28 | 481:108 (4.1e-57) | POWERED, V1 3/3 · X 0/3 | **(i)** | 195 | 정의 안 됨 (범위 밖: 0.9105) | 0.382 [0.347, 0.415] |
| ALDv-pilot | +9 / +12 / +15 | 108:39 · 126:35 · 164:27 | 398:101 (1.1e-42) | POWERED, V1 3/3 · X 0/3 | **(i)** | 209 | 정의 안 됨 (범위 밖: 0.9160) | 0.330 [0.295, 0.364] |
| SBL-loop | +9 / +12 / +15 | 235:42 · 211:26 · 212:38 | 658:106 (4.2e-98) | POWERED, V1 3/3 · X 0/3 | **(i)** | 136 | 0.264 [0.220, 0.305] | 0.478 [0.448, 0.508] |
| SBL-pilot | +9 / +12 / +15 | 247:43 · 218:25 · 230:32 | 695:100 (2e-110) | POWERED, V1 3/3 · X 0/3 | **(i)** | 219 | 정의 안 됨 (범위 밖: 0.9199) | 0.497 [0.466, 0.527] |
| OMP-pilot | +9 / +12 / +15 | 396:32 · 411:13 · 481:6 | 1288:51 (1.2e-310) | POWERED, V1 3/3 · X 0/3 | **(i)** | 177 | 정의 안 됨 (범위 밖: 0.9035) | 0.672 [0.652, 0.693] |

- **요약 줄(원문)**: `SUMMARY-B (baselines without b*, 15): (i) 14, (ii) 0, not decided 1; b* -> V1 (i)` · `SUMMARY registered baselines 16 (b* + 𝔅 15): (i) 15, (ii) 0, not decided 1`.
- **"전부" 문장: 쓰지 않는다**(§1 조건 불충족). 그대로 적는 것: **(i) 14 / 15 (b\* 포함 15 / 16), (ii) 0; (i) 가 아닌 arm = `V1-pilot` (iii) "판정하지 못함 (유의 방향 없음)"** — 35:25 (p 0.25) · 21:9 (0.043) · 14:8 (0.29), pooled 70:42 (p 0.01), POWERED, V1 이 1/3 점에서만 유의. §1 이 금지한 동치 문구는 쓰지 않는다.
- **"멀어진다" 문장: 쓰지 않는다** — `'등록된 baseline 전부와 멀어진다' condition (k = 16, (ii) = 0, R_X* CI lower > 0): NOT met` (X\* = M-ours-bstar, F = 2232; R_X\*(−3 dB) = 0.202 [0.166, 0.240] 이나 (i) 가 16 개 중 15 개(k = 15 ≠ 16)라 조건 불충족).
- **드리프트 검사**: `b* → V1` 을 `pair_baselines` 가 다시 낸 값(127:46 · 111:42 · 119:36, pooled 357:124, (i), R 0.202 [0.166, 0.240], 판정점 합 0.279 [0.241, 0.316]) = DMC16e4 §6.1 → 드리프트 없음.
- SNR@0.1 격차는 16 쌍 모두 n/a (두 arm 모두 > 15 dB). R_X(−3 dB) 는 X 의 −3 dB BLER 이 0.9 를 넘는 **11 개**(R0-pilot@1 · R1-turbo · R2-ours-G · R3-bigamp · R4-llr · R4-scvamp · bstar-pilot · ALD-pilot · ALDv-pilot · SBL-pilot · OMP-pilot)에서 정의되지 않는다(포화 가드); 정의되는 5 개 = b\* · b\*-scalar · gmm32 · V1-pilot · SBL-loop [감사 M1 정정: 처음에는 "10 개" 로 잘못 셌다].
- 라벨에 붙는 것(§1): DMC16e4 §1 "DMC 고유 사항" (1)(2)(3) — 유한 풀(테스트 52,172 쌍 복원 추출) · 누수 0.433 · outage(genie BLER −3 dB 0.686) — 과 "DMC 고유 1"(조정용 개발 채널이 테스트 풀에서 나옴; baseline 에 유리한 방향). 범위: 이 풀·이 split·이 크기 한정.

### 6.2 원고 범례 11 곡선 — BLER@16 실패 수 / 2560 (`pairB_SPDMC.txt` 의 표; 전 SNR n = 2560)

| 곡선 | −3 | 0 | +3 | +6 | +9 | +12 | +15 dB |
|---|---|---|---|---|---|---|---|
| Proposed (V1) | 2136 | 1742 | 1505 | 1281 | 1142 | 952 | 801 |
| Annealed Langevin (plug-in) = ALD-pilot | 2331 | 1910 | 1610 | 1366 | 1222 | 1065 | 981 |
| GMM prior = b\* | 2232 | 1826 | 1586 | 1372 | 1223 | 1021 | 884 |
| Gaussian prior = R2-ours-G | 2330 | 2050 | 1801 | 1592 | 1440 | 1209 | 1090 |
| Turbo LMMSE = R1-turbo | 2451 | 2246 | 1976 | 1739 | 1532 | 1293 | 1158 |
| BiG-AMP = R3-bigamp | 2461 | 2224 | 2028 | 1913 | 1929 | 1910 | 1957 |
| Pilot-only LMMSE = R0-pilot@1 | 2527 | 2413 | 2227 | 2077 | 1913 | 1705 | 1590 |
| SBL (in loop) | 2272 | 1969 | 1710 | 1504 | 1335 | 1137 | 975 |
| SBL (pilot-only) | 2355 | 2021 | 1743 | 1523 | 1346 | 1145 | 999 |
| OMP (pilot-only) | 2313 | 2039 | 1800 | 1618 | 1506 | 1350 | 1276 |
| Perfect CSI = genie | 1756 | 1457 | 1238 | 1048 | 927 | 754 | 611 |

- 11 곡선에 없는 등록 arm (같은 순서): V1-pilot 2256 / 1837 / 1559 / 1311 / 1152 / 964 / 807; bstar-pilot 2323 / 1933 / 1637 / 1391 / 1237 / 1040 / 903; ALDv-pilot 2345 / 1927 / 1621 / 1363 / 1211 / 1043 / 938; M-ours-bstar-scalar 2249 / 1837 / 1597 / 1383 / 1220 / 1020 / 887; M-ours-gmm32 2270 / 1951 / 1693 / 1463 / 1325 / 1106 / 973; R4-scvamp 2477 / 2322 / 2125 / 1978 / 1820 / 1656 / 1554; R4-llr 2523 / 2455 / 2358 / 2266 / 2184 / 2025 / 1945.
- 그림: `conference/figures/F21dmc_col.{pdf,png}` (`paper_f21dmc.py`, 기록 `records/paper_f21dmc.txt`): 실패 수 = 위 표(assert), 세 raw 의 Perfect CSI 오류 배열 동일(assert), 그려진 baseline 9 개의 라벨 모두 (i), 제안 곡선 이하인 그려진 **baseline** 곡선 없음(Perfect CSI 제외; 점추정).

### 6.3 보고 전용

- `pair_PILDMC.txt` (PILOT16e4 형식): P1 `V1-pilot → V1` (iii) (위와 같은 계수); P2 `bstar-pilot → V1-pilot` 136:51 · 121:45 · 126:30, pooled 383:126 → (i); `bstar-pilot → b*` 44:30 · 36:17 · 35:16 → (i) (2/3); `V1-pilot → b*` 50:121 · 51:108 · 40:117, pooled 141:346 → (ii) (V1-pilot 이 3/3 에서 적게 실패).
- `pair_ALDDMC.txt` (ALD16e4 형식): A1 `ALDv-pilot → V1` 108:39 · 126:35 · 164:27 → (i); A2 `ALD-pilot → V1` 123:43 · 150:37 · 208:28 → (i); A3 `ALDv-pilot → V1-pilot` 104:45 · 113:34 · 158:27, pooled 375:106 → (i); `ALDv-pilot → b*` 97:109 · 103:81 · 124:70 → (iii); `bstar-pilot → ALDv-pilot` 120:94 · 89:92 · 76:111 → (iii); `ALD-pilot → ALDv-pilot` 38:27 · 40:18 · 64:21 → (i) (2/3). 시험 ALD NMSE(추정 파일 평균) −8.07 / −10.94 / −13.41 / −16.22 / −18.99 / −21.26 / −23.92 dB.
- 조정 표: §5 (SBL ρ 8; OMP ρ 16 = 격자 끝 + 캐비엇; ALD c 0.01 · β 0.005).
- raised trials: PIL 0 / 0, ALD 0, SP 0 / 0 / 0.
- **등록 외 진단(보고 전용 — 라벨·검정·CI 없음; 결과를 본 뒤 사용자 질문으로 한 사후 분할)**: `results/review_next/DMCB16e4_genie_rank.txt` (`prereg_audit_2026-10-10/genie_rank.py`) — 주 실행의 시행을 채널의 최대 특이값 에너지 비중으로 나눈 Perfect CSI · V1 · b\* 의 BLER@16 (주 실행의 진단; 같은 공개를 DMC16e4 §6.4 에 둔다; 스크립트는 감사 산출물이 아니라 이 세션이 쓴 것).

### 6.4 §2 예측 채점

1. "(ii) 0 이고 (i) ≥ 13" → **적중** ((ii) 0, (i) 14 / 15). (i) 가 아닐 후보로 적은 둘 가운데 `V1-pilot` 이 (iii), `bstar-pilot` 은 (i).
2. 조정: OMP 의 L 이 −3 · 0 dB 에서 ≤ 4 → **적중** (2 / 2; §5). BLER(6.2 의 표): −3 · 0 dB 에서 `OMP-pilot` < `R0-pilot@1` (2313 < 2527, 2039 < 2413) 이고 `SBL-pilot` < `R0-pilot@1` (2355 < 2527, 2021 < 2413) → **적중**.
3. −3 · 0 · +3 dB 모두 `ALD-pilot` > `V1-pilot` 실패 수 (2331 > 2256, 1910 > 1837, 1610 > 1559) → **적중**; `pair_ALDDMC.txt` A3 = (i) → **적중**.
4. 빗나갈 경로((ii) 가 하나라도): 미발동.

### 6.5 기록 감사 (Fable 5.1 서브에이전트, 2026-10-10 23:11 CDT 보고; `prereg_audit_2026-10-10/audit_DMCBASE16e4.md`, 재계산 `recompute_dmcbase.py` → `recompute_dmcbase.out`, 등록 도구 재실행 `rerun_pairB_SPDMC.txt`)

감사 대상 = 커밋 3e91b94b 의 §4·§5·§6. 독립 재계산(네 raw 를 numpy 로 직접 읽음; `pair_baselines.py` 미사용, `pairB_SPDMC.txt` 미열람; 부트스트랩 재구현): 자동 비교 521 값 중 **불일치 1** (아래 M1 — 본문 한 줄의 개수; 표·라벨은 일치); 등록 도구 재실행은 머리말 줄을 빼고 커밋본과 바이트 동일. **16 라벨 전부 재현**(V1-pilot (iii) 포함), "전부"·"멀어진다" 문장 보류가 §1 규칙과 일치, 드리프트 없음, §2 예측 채점 전부 재현. 무결성: 청크 계획, raw 마다 깨끗한 커밋 하나(27737b62 / 3ddb0831 / 5aa7b9b4 / ff736ea2), R5-genie 세 raw 가 주 실행과 비트 동일, `meta|sparse` 448 청크 = pick, pick = `per_snr_pick(tune)`, sha 7 개, ALD 추정 파일의 출처 = `tune_PILDMC.json`. 편차(단계 순서·단계 사이 커밋·부분 결과 열람)는 로그·git 과 일치하고, 단계가 서로의 출력을 읽지 않아 순서가 수치를 바꿀 수 없음을 확인.

**MUST 1 · SHOULD 2 · NIT 7 — 모두 반영(라벨·표의 수치 불변; 기록 2026-10-10 23:13 CDT, Opus 5.5)**: M1 §6.1 본문의 "R_X(−3 dB) 가 정의되지 않는 baseline 수" 10 → 11 (표는 처음부터 11 행); S1 등록 외 진단(`DMCB16e4_genie_rank.txt`)의 공개를 DMC16e4 §6.4 에도 추가; S2 "제안 곡선 이하인 그려진 곡선 없음" → "baseline 곡선(Perfect CSI 제외)" (이 기록과 `paper_f21dmc.py` 의 기록 문구; 그림·수치 불변, 기록 재생성); N1 k 표현; N2 §4 의 §5 채움 시각; N3 ALD 시험 사이트 파일 재사용; N4 "로그 외 사실" 표시; N5 `docs/EXPERIMENTS.md` 행; N6 전사 커밋 해시; N7 금지 문구를 글자로 옮기지 않게 수정. 감사가 확인하지 못한 것: GPU 점유·컨텍스트 시도·`nvidia-smi` 확인(로그 산출물 없음), 사용자 인용의 원문, ALD 추정의 GPU 결정성(코드의 assert 만 확인).
