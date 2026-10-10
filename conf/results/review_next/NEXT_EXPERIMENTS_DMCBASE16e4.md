# NEXT_EXPERIMENTS_DMCBASE16e4 — DeepMIMO (prior DMC, 셀 C2, N′ = 1.6e5) 에서 **등록된 baseline 전부**: PILOT16e4·ALD16e4·SPARSE16e4 의 절차를 DMC 한 행에 그대로 적용 (태그 PILDMC / ALDDMC / SPDMC) — 사전 등록 v1 (초안)

- 작성: 2026-10-10 18:39 CDT (= 10-11 08:39 KST), Claude Code (Opus 5.5), 초안 v1. 적대적 검토(Fable 서브에이전트) 반영 뒤 v2 로 동결한다. 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). 커밋 뒤에는 §1~§2 를 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 지시(2026-10-10 CDT, 이 세션): "Deepmimo로 다른 baseline들도 실험해야지. 우리 conference에 넣는 11개 그래프 모두 찍어야 해. 우선 하던거 마무리하고 진행하자".
- **작성 시점 공개**: DMC 의 수신기 BLER 은 **아직 한 번도 관측되지 않았다** — 주 실행 `DMCB16e4` (`NEXT_EXPERIMENTS_DMC16e4.md` v2, 동결 9d4c3b4a) 은 학습이 아직 돌고 있고(epoch 490) GB′·§5·실행이 남았다. 작성자가 본 DMC 의 것: testbed 통계(`results/testbed_DMC.txt`), 학습 곡선, GMM 격자와 b\* (kron 4096, ll_val 122.37953759128766; `logs/tb2_post_DMC.log`). 희소 baseline 조정(`sparse_tune.py --prior DMC --cell C2`, 개발 NMSE, BLER 없음)은 10-10 18:35 CDT 에 시작해 돌고 있고 아직 어떤 점수도 읽지 않았다. **이 v1 은 주 실행의 BLER 이 시작되기 전에 커밋한다**; 검토·v2 동결은 주 실행과 겹칠 수 있다(겹치면 동결 줄에 그때 무엇이 관측돼 있었는지 적는다). 이 문서의 실행은 주 실행이 끝나고 수용 검사를 통과한 뒤다.
- 목적: 원고 범례의 11 곡선(`conference/figures/paper_f16deep.py` `SHOW` = V1, ALD-pilot, b\*, R2-ours-G, R1-turbo, R3-bigamp, R0-pilot@1, SBL-loop, SBL-pilot, OMP-pilot, genie)을 DeepMIMO 에서도 모두 잰다. 주 실행(14 arm)이 일곱을 내고 **넷이 빠진다: ALD-pilot, SBL-loop, SBL-pilot, OMP-pilot**. `PIL` (V1-pilot, bstar-pilot) 은 11 곡선에 없지만 baseline 집합(𝔅 12 + 희소 3)을 다른 데이터셋과 같게 하려고 함께 돌린다(`pair_baselines.py`·`pair_ald.py` 가 그 raw 를 읽는다).
- 틀(새 규칙 없음): `NEXT_EXPERIMENTS_PILOT16e4.md` §1, `NEXT_EXPERIMENTS_ALD16e4.md` §1(조정 격자·끝 규칙·β 규칙·멈춤 단계·v 는 `code/ald.py` 에 고정), `NEXT_EXPERIMENTS_SPARSE16e4.md` §1(arm 정의·`per_snr_pick`·v2b 격자), `NEXT_EXPERIMENTS_STATIC16e4.md`·`NEXT_EXPERIMENTS_SUPP16e4.md` §1(표 B `X → V1`·라벨·X\*·R_X·가드, `pair_baselines --provenance manifest`). 다른 곳은 아래 "DMC 고유" 두 칸뿐이다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **시행·크기 (기존 실험과 같은 크기)** | 주 실행과 **같은 테스트 시행 0..2559** (prior DMC, PID 11 의 시행 스트림 → **주 실행 `raw_DMCB16e4` 와 시행 단위로 짝**), 셀 C2 (8×4, T 16, Tp 4), n = 2560, chunk 40, 7 SNR (−3..15 dB; 결과 뒤 늘리지 않는다), 16 반복, 수신기 CPU complex128. 가중치 = DMC16e4 §5 의 V1 `_best` 체크포인트(sha 는 §5), GMM = 주 실행의 b\* 적합(kron 4096; fits 링크 `gmm_fits_D2_{PILDMC,ALDDMC,SPDMC}` → `gmm_fits_D2_DMCB16e4`), N′ = 160000 |
| **arm 과 절차** | **PIL** (PILOT16e4 §1): `V1-pilot`, `bstar-pilot`, `R5-genie`, `runner.py run … --pilot-arms --tag PILDMC`. **ALD** (ALD16e4 §1): Arvinte–Tamir annealed Langevin 파일럿 추정(같은 V1 `_best` 가중치)을 GPU 로 사전 계산(`ald.py regen` → `tune`(개발) → `estimate`(테스트); 01_RULES §9.3 예외는 ALD16e4 와 같음), 수신기는 CPU: `ALD-pilot`, `ALDv-pilot`, `R5-genie`, `--ald-file results/ald/ald_PILDMC.npz --tag ALDDMC`; 조정은 `ald.py tune` 이 하는 그대로(c 격자 × β 격자, 끝이면 그 축 한 단계씩 최대 2 회 확장, β 규칙(저자 기본값 0.005 가 0.03 dB 안이면 유지), 멈춤 단계 = SNR 별 개발 평균 NMSE 최소, v = 그 단계의 개발 MSE/원소). **SPARSE** (SPARSE16e4 §1): `SBL-loop`, `SBL-pilot`, `OMP-pilot`, `R5-genie`, `--sparse-file results/sparse/pick_DMC_C2.json --tag SPDMC`; 하이퍼파라미터 = `sparse_tune.py --prior DMC --cell C2 --n 256` 의 `per_snr_pick` (v2b 격자 ρ {1,2,4,8,16}, n_em {1,2,3,5,10,25,50}, L {1,…,64}, L ≤ N), **격자 한 판으로 끝낸다 — 고른 값이 격자 끝이면 끝값 + 캐비엇, 더 확장하지 않는다**(SPARSE16e4 §1 의 C6 처리와 같음) |
| **DMC 고유 1 — 개발 채널은 테스트 풀에서 나온다** | ALD 의 개발 시행 = 시행 스트림의 2560..3071 (n = 512; 다른 데이터셋과 같은 정의) → DMC 에서는 테스트 풀 복원 추출. SPARSE 의 개발 채널 = 전용 스트림 `default_rng([20260930, TBID, PID, Nr, snr+100])`, n = 256/SNR → DMC 에서는 테스트 풀 복원 추출(`dmimo._which`, 커밋 ae880c27 — DMC16e4 동결 뒤·BLER 전의 추가이며 기존 스트림은 그대로). 둘 다 테스트 시행 0..2559 와 **다른 추첨**이지만 풀이 유한(52,172 쌍)이라 같은 쌍이 겹칠 수 있다 — 한 SNR 의 2560 테스트 시행이 덮는 쌍의 비율 1 − e^(−2560/52172) ≈ 0.048 → 개발 512 중 약 25 쌍, 256 중 약 12 쌍(채널은 같고 잡음은 다름). 다른 데이터셋에서 개발 채널이 테스트와 같은 생성기에서 나오는 것과 같은 처지이며 **baseline 에 유리한 방향**이다; V1·b\* 의 학습·선택은 학습 타일 안에서만 한다(DMC16e4 §1 (7)). 조정 점수는 채널 추정 NMSE 뿐이다(BLER 없음) |
| **DMC 고유 2 — 앞선 라벨 기록이 없다** | 다른 데이터셋의 `run_sparse16e4.sh` 는 STATIC16e4 가 적은 𝔅 12 라벨을 `--expect` 로 기계 대조했다. DMC 에는 STATIC16e4 행이 없으므로 `--expect`·`--expect-bstar` 없이 한 번에 15 개를 모두 새로 계산한다 |
| **실행** | `code/run_dmc_base.sh <ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16>` (인자는 §5 가 기록한 값만). 전제(스크립트가 검사): 이 문서·`DECISIONS.md`·pick·tune JSON·`results/ald/tune_PILDMC.json` 이 git 추적 + clean, `conf/code`·`Demo` clean, 주 실행 `PRIOR_EVAL_DONE` 과 `DMCB16e4_accept.txt` = `ACCEPT: OK`, 체크포인트·pick·ALD 조정 기록의 sha = §5. 순서 **PIL → ALD → SP → pair_baselines**; 단계의 수용 검사가 실패하면 거기서 멈춘다(그 단계 무효, 원인 기록). GPU 는 ALD 추정에만 한 장(빈 GPU 가 없으면 멈춤, 재시도 없음). 로그 `logs/run_dmc_base.log`, 끝 표시 `DMC_BASE_DONE`. **실행 중 main 커밋 금지**(raw 의 `run\|git` 은 한 커밋) |
| **수용 검사** | 태그마다 `eval_accept.py` (청크 {(40k, 40): k = 0..63} × 7 SNR, meta `ntrain`·`bstar`·`kron_K`·`ll_val`, 체크포인트 sha·role(PIL·ALD), 16 반복, **R5-genie 가 `raw_DMCB16e4` 와 7 SNR 전 시행 비트 동일**); PIL: `pair_cross.py` 무결성; ALD: `pair_ald.py` 무결성(추정 파일·시행 정렬); SP: pick 이 `per_snr_pick` 으로 재현되고 tune JSON 이 prior DMC·cell C2·n 256·v2b 격자, 메모리 가드, 모든 청크의 `meta\|sparse` = 그 SNR 의 pick |
| **판정** | `pair_baselines.py --base raw_DMCB16e4 --pil raw_PILDMC --ald raw_ALDDMC --est PILDMC --extra raw_SPDMC --add-baselines SBL-loop SBL-pilot OMP-pilot --cell C2 --prior DMC --r0 at1 --provenance manifest` → 표 B `X → V1`, X ∈ 𝔅 15 = {M-ours-bstar-scalar, M-ours-gmm32, R0-pilot@1, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, bstar-pilot, V1-pilot, ALD-pilot, ALDv-pilot, SBL-loop, SBL-pilot, OMP-pilot} → **새 라벨 15 개**. 라벨·판정점(앵커 = X, BLER@16 이 [0.005, 0.9] 안에서 0.1 에 가장 가까운 3 SNR)·power guard·X\*·R_X·가드는 SUPP16e4 §1 그대로: (i) = POWERED 이고 V1 이 ≥ 2/3 점에서 적게 실패, (ii) = X 가 ≥ 2/3, (iii) = 방향 없음, (iv) = 검정력 미달. `b* → V1` 은 DMC16e4 §6 의 라벨을 인용한다(같은 raw 에서 `pair_baselines` 가 다시 낸 값이 다르면 드리프트로 적는다). 출력 `results/review_next/pairB_SPDMC.txt` |
| **"전부" 문장** | DMC16e4 의 `b* → V1` 이 (i) **이고** 15 개가 모두 (i) → "DeepMIMO (6 개 도시 28 GHz, block split) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)". 아니면 (i) 의 수와 (i) 가 아닌 arm 의 이름·라벨을 그대로 적고 "전부" 를 쓰지 않는다. (ii)(iii)(iv) 에서 "비긴다"·"동등" 문구를 만들지 않는다. 모든 문장에 DMC16e4 §1 "DMC 고유 사항" (1)(2)(3)(유한 풀·누수 0.433·outage)과 위 "DMC 고유 1" 을 붙인다. 범위: 이 풀·이 split·이 크기 한정 |
| **다중성** | 새 라벨 15 개 + 인용 1 개; 등록 사이 보정 없음(다른 데이터셋과 같은 관례 — 원고에서 등록 검정 수를 밝힌다) |
| **그림** | DMC 의 11 곡선은 전 SNR n = 2560 으로 그린다. 다른 데이터셋의 고 SNR 보강(FIGHS16e4, +6..+15 dB n = 20480)은 DMC 에 하지 않는다 — 하려면 별도 등록 |
| 보고 전용 | ALD 조정 표(`results/ald/tune_PILDMC.json`: c, β, 멈춤 단계, v, 개발 NMSE), SPARSE 조정 표·끝값 여부, raised trials 수, `pair_cross`·`pair_ald` 의 등록 비교(다른 데이터셋과 같은 형식; 새 라벨로 세지 않는다). 누수 층화는 주 실행(b\*·V1·genie)에만 있고 baseline 으로 넓히지 않는다 |
| 비용 [추정] | SPARSE 조정 CPU 2 스레드 ≈ 3.3 h (UMi28 실측 11,872 s); ALD 조정·추정 GPU 한 장 ≈ 10 분; PIL ≈ 10 분·ALD ≈ 5 분·SP ≈ 30 분(CPU 192 워커; 6 데이터셋 실측 38 분·11 분·78 분에서) |

## 2. 미리 적는 예측 (빗나가면 그대로 쓴다; DMC 의 BLER 은 본 적이 없다)

1. 15 개 가운데 **(ii) 는 0 개, (i) 는 13 개 이상**. 확신 중간(선례: D2 C2·D3·UMi28·MIX3 에서 15/15 (i); SV8e·C6 에서 pilot-only 일부가 (iv)). (i) 가 아닐 후보는 `V1-pilot`·`bstar-pilot` (루프의 이득이 작을 때).
2. 희소 baseline: OMP 의 L 은 낮은 SNR 에서 작다(≤ 4; 유효 경로 수 중앙값 1.7) — 조정 결과이며 BLER 예측이 아니다. `OMP-pilot`·`SBL-pilot` 은 `R0-pilot@1` 보다 적게 실패한다(낮은 SNR).
3. `ALD-pilot` 은 `V1-pilot` 보다 많이 실패한다(다른 6 데이터셋과 같은 방향).
4. 빗나갈 경로: (ii) 가 하나라도 나오면 그대로 적는다 — 조정을 다시 하지 않고, 격자를 늘리지 않고, 사후 설명은 사용자.

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 |
|---|---|
| `dmimo._which` 에 sparse_tune 개발 스트림 → 테스트 풀, `run_dmc_sparse_tune.sh` | 완료·커밋 ae880c27 |
| SPARSE 조정 (tmux `sptdmc`, CPU 2 스레드) | 진행 중: 10-10 18:35 CDT 시작 → `results/sparse/{tune,pick}_DMC_C2.json` |
| `run_dmc_base.sh` (세 스크립트의 행 본문을 DMC 한 행으로) | 이 커밋 |
| ALD 개발 사이트 재생성·조정 (`ald.py regen --set dev`, `ald.py tune`; GPU 한 장) | 대기: V1 `_best` 체크포인트(학습 종료) 뒤 |
| 적대적 검토(Fable) → v2 → 동결 커밋 | 대기 |
| 주 실행 DMCB16e4 `PRIOR_EVAL_DONE`·ACCEPT OK → §5 → `run_dmc_base.sh` → §6 → 기록 감사(Fable) | 대기 |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다)

(체크포인트 stem·sha, pick·tune JSON sha, ALD 조정 기록 sha 와 고른 값(c, β, 멈춤 단계, v), SPARSE 고른 값(ρ, SNR 별 n_em·L, 끝값 여부), 스크립트 인자 원문.)

## 6. 결과 (실행 뒤 전사)

(실행 뒤 채운다.)
