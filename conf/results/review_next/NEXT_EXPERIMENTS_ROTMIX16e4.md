# NEXT_EXPERIMENTS_ROTMIX16e4 — 표류로 학습한 prior (B′, S2d): 수신 배열 회전 0°/15°/30° 의 S2 채널에서 V1 대 b\* 와 등록된 baseline 전부, 정적 학습(ROT16e4 시행)과 짝 비교 (사전 등록 v2)

- 작성: 2026-09-27 22:39 CDT (= 09-28 12:39 KST) 초안 v1 (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 6·권고 12; `prereg_reviews_2026-09-27/review_ROTMIX16e4.md`) 반영 v2 2026-09-27 23:26 CDT (Fable 5.1). **동결은 두 단계**(검토 반드시 1): **설계 동결 = 브랜치 `c-rotmix`(worktree `~/t2_wtB`) 의 이 커밋**(§1~§3 불변; ROT16e4 실행 중이라 main HEAD 를 바꾸지 않는다); §5 의 GB′·병합 diff·선행 코드 해시는 "설계 동결 뒤·BLER 전" 의 별도 커밋으로 채운다(ALD 조정은 이미 §5 에 있다). 병합은 ROT 종료 뒤; `git diff <설계 동결> <병합> --stat -- conf/code Demo` 출력을 §5 에. 커밋 뒤 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_ROT16e4.md` (같은 회전 모델·같은 시행, pair_rot), `NEXT_EXPERIMENTS_MISMATCH16e4.md` (`--train-prior` 경로: 학습 prior ≠ 시험 prior, 이름 바꾼 fits 링크, 적합 지문), `NEXT_EXPERIMENTS_S2V16e4.md` v2 (baseline 집합 𝔅, baseline 별 회수율, X\* 규칙), `NEXT_EXPERIMENTS_PILOT16e4.md`·`_ALD16e4.md`, `08_SPEC_analysis.md` §2 표 B, `01_RULES` :76·:77.
- **작성 시점 공개**: 사용자 요청(2026-09-27 13:46 CDT) "비정상 데이터로 학습해서 V1 이 GMM 대비 이득을 얻게" — A/B 강건성 검정용 표류 학습 prior; 순서 결정 "A, B, B′, C 먼저"(14:17 CDT); "14 arm 전부 + ALD, baseline 마다 genie 격차 회수율"(14:17 CDT); 사용자 목표 "제안 prior 가 genie 에 가깝고 **모든** baseline(GMM·학습 방법)과 멀어지게 — 사전 등록·동일 예산·감사된 방법으로만"(09-28 재확인); 검토 뒤 결정(09-27 23:2x CDT): DD-δ 라벨 등록, last 태그 3 개 추가, 같은 K 대조 태그 3 개 추가, 𝔅 에 V1-pilot 포함(S2V 와 공통). **01_RULES :77 과의 긴장은 여기서 해소한다**: 요청의 동기는 위처럼 정직하게 인용하고, 검정은 **양방향**이다 — "표류를 포함한 학습 분포가 두 prior 에 **같은 데이터로** 주어질 때 V1 이 GMM 보다 더 얻는지 / 덜 얻는지"(DD 라벨은 "덜 얻는다" 도 낸다). 설계는 결과 전에 고정됐다: S2d 코드 2640bb87, 큐 시작 09-27 13:46 CDT(dca8d19c); δ 범위 = ROT 의 등록 각 30° 재사용(조정 없음). 작성 시점에 본 것: 정적·PILOT·MISMATCH·ALD·SEEDS·DOP 결과와 **ROT16e4 의 수용·무결성 줄(라벨 아님)**. **ROT 노출(사실대로)**: 설계 동결 시각에 `pair_ROTaB16e4k.txt`·`pair_ROTbB16e4k.txt`·`pair_ROTaNR16.txt` 3 개가 존재했고(§5 에 수 기록), 등록자·검토자 모두 내용을 열지 않았다(로그의 `rc=` 줄만). S2d 가중치·적합은 어떤 BLER 로도 평가된 적 없다(σ 격자 측정은 Gaussian 수신기·ν_q 만, C1·C2).
- 목적: ROT16e4 는 0° 로 학습한 prior 를 회전된 채널에서 잰다(공변량 이동). 여기서는 **학습 분포 자체가 표류를 포함**하도록(블록마다 회전 δ ~ U[0°, 30°]) 같은 예산 N′ = 1.6e5 로 V1 과 GMM 을 **둘 다** 다시 학습·적합하고, 고정 회전 0°/15°/30° 의 S2 채널(ROT·base raw 와 같은 시행)에서 (1) 표류 학습 V1 이 표류 학습 b\* 와 등록된 baseline 전부보다 적게 실패하는지(RB, 판정 3), (2) 표류 학습이 정적 학습보다 V1 에·b\* 에 각각 도움이 됐는지(DT), (3) **V1 의 genie 격차 회수율이 b\* 대비 얼마나 달라졌는지(DD)** 를 잰다. 헤드라인·ROT 라벨은 바뀌지 않는다.

---

## 0. 모델 (고정)

- **S2d** (`code/d2.py`, 브랜치 c-rotmix 2640bb87; PID 10 = 새 스트림): S2 기하 + 블록 공통 수신 배열 회전 δ ~ U[0, 30°] (`DRIFT`; 모든 경로 AoA θ_l + δ), **블록의 마지막 추출**(th·ph·al·L 뒤; 다른 prior 의 스트림 불변 — `selftest_s2d` OK, 검토자 재실행). 송신각 불변 → Rt(파일럿 규칙) 불변; 실행 prior 가 S2 라 `make_pilots(S2)` — 두 이유로 파일럿은 S2 와 같은 행렬. 전력은 조향 벡터 단위 노름이라 항등.
- **시험 채널**: prior **S2** 에 ROT16e4 의 고정 회전 δ ∈ {0°, 15°, 30°} (`runner.py --rotation`). 시행 스트림 = 기준 raw `raw_B16e4k` (0°) = `raw_ROTaB16e4k` (15°) = `raw_ROTbB16e4k` (30°) 의 시행 — 회전은 난수를 소비하지 않고 `--train-prior` 는 스트림·파일럿·생성기를 건드리지 않으므로 genie 는 δ 별 기준 raw 와 비트 동일해야 한다(짝의 전제·무결성 검사; prior 적용의 증명은 별도 — §1 수용 (c)(d)(e)).
- **학습 범위와 시험 각**: S2d 의 AoA 주변 분포는 S2 부채꼴 ⊛ U[0°, 30°] (−60°…90° 사다리꼴). 시험 δ = 30° 의 블록(모든 경로가 [−30°, 90°])은 δ 분포의 **끝점 성분**이고 0° 도 끝점, 15° 가 중심 — 지지집합 안이지만 블록 단위로는 가장자리. S2d 는 δ 를 모르는 **혼합 prior** 라 δ 를 아는 prior 보다 nuisance 비용을 낸다(두 prior 에 공통 → RB 는 공정). "보지 못한 표류에 대한 일반화" 가 아니라 "표류를 포함한 분포로 학습했을 때" 의 측정이다. δ 추정·각도별 재학습은 범위 밖.
- **정적 쪽(기준 raw)의 prior**: V1 = 헤드라인 체크포인트 `d2sx_N160000_a1.pt` (legacy-last; best 파일 없음), GMM b\* = kron K = 1024 (기본 격자 끝, B32e4 §1 캐비엇 "K = 2048 미적합"; 확장 규칙은 그 뒤 도입) — ROT16e4 와 같다. 이 비대칭 둘을 last 태그·같은 K 대조 태그로 맞춘다(§1).
- 등록 전 관측(BLER 아님): 학습 1368 epoch patience (best 1348, val 3.482288e-01), 발산 없음; GMM b\* = kron K = 4096 (ll_val −5.574511189627533; kron 1024 → 2048 → 4096 순서로 격자 끝 → 병합, 4096 에서 멈춤 — 사용자 결정 09-26 (3), D3·MIX3·UMi28 선례; §5), full 최고 512 (b\* 가 kron 이므로 full 1024 규칙 미발동 — B32e4 §1 "그 계열 최대 K" 문구, 검토 확인). GB′ = [§5, 실행 중].

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산** | D2 C2 = Nr 8, Nt 4, T 16, Tp 4, K = 42, 7 SNR (−3…+15; 결과 뒤 격자 확장 없음), n = 2560, 시험 시행 0..2559. N′ = 160000: `arms.training_set("D2","S2d",8,4,160000)` (스트림 7) 를 GMM 적합(`run_s2d.sh`)과 score 학습(`run_d2_sx.py --prior S2d`, 자체 9:1)이 함께 쓴다 — 동일 예산(검토 확인) |
| **지위** | UNGATED 측정(SV8e·ROT 선례). 헤드라인(B16e4k)·ROT 라벨 불변 |
| **가중치·적합** | V1 `_best` = `ckpt/d2sx_S2d_N160000_a1_best.pt` (sha256[:16] **ceec0222e0912a1c**, epoch 1348, `prior='S2d'`) — RB·판정 3 의 가중치; V1 last-EMA = `ckpt/d2sx_S2d_N160000_a1.pt` (**98bc88f7333f19ee**, ep 1368) — DT-V1·DD 의 가중치(정적 legacy-last 와 역할 일치). GMM: 격자 full {16..512} · kron {16..4096}, `results/gmm_fits_D2_S2dB16e4/`; b\* = kron 4096 (ll_val −5.574511189627533; RB·판정 3·DD); **같은 K 대조** b\*₁₀₂₄ = kron 1024 (ll_val −8.988496590420036; DT-b\*). σ 격자 `S2d` (`results/sigma_grid_D2_S2d.txt`, 09-28 03:45 KST, 2640bb87, C1+C2; 커밋됨). 경로는 main 기준(병합 뒤 이동, §4) |
| **fits 링크 디렉터리 (손으로 만듦; 커밋 대상 아님; mtime §5)** | 태그마다 하나, S2d 적합을 S2 이름으로: `gmm_fits_D2_<태그>/fit_S2_Nr8_<계열>K<K>_n160000.npz → ../gmm_fits_D2_S2dB16e4/fit_S2d_…` — 14 arm·PIL·ALD·last 태그는 15 링크(full 6 + kron 9); **k1 태그는 13 링크(full 6 + kron 16..1024)** → `gmm_selection` 이 kron 1024 를 고른다. ALD 조정용 `gmm_fits_D2_RMXS2d` (15 링크, 09-27 22:5x CDT 생성) 는 ALD 의 `--fits-tag` 로 재사용 |
| **태그 (δ ∈ {0, 15, 30} × 5 = 15 개; 이름 `RMX0…`, `RMX15…`, `RMX30…`)** | 공통 인자 `--testbed D2 --prior S2 --cell C2 --train-prior S2d --rotation <δ> --n 2560 --chunk 40 --ntrain 160000` (δ = 0 도 `--rotation 0`). (A) `RMX<δ>`: `--stagec-ckpt …_a1_best.pt`, 14 arm (S2V §1 ① 목록; GMM·Gaussian arm 은 S2d 적합, V0/V1/V4/V4b 는 S2d `_best`; R3-bigamp 는 prior 무관). (B) `RMX<δ>PIL`: `_best`, `--pilot-arms --arm V1-pilot bstar-pilot R5-genie`. (C) `RMX<δ>ALD`: `_best`, `--ald-file results/ald/ald_RMX<δ>ALD.npz --arm ALD-pilot ALDv-pilot R5-genie`. (D) `RMX<δ>last`: `--stagec-ckpt …_a1.pt` (last-EMA), `--arm M-ours-dscore-C-V1 R5-genie`. (E) `RMX<δ>k1`: `_best`, 링크 13 개 디렉터리, `--arm M-ours-bstar R5-genie`. 순서: δ 마다 (A) → (B) → (C) → (D) → (E); (A) 가 ABORT 이면 그 δ 의 나머지를 시작하지 않는다 |
| **ALD 사전 계산 (δ 마다; ALD16e4 §0·§1 절차 그대로)** | 조정 = `ald.py regen --tag RMX<δ>ALD --prior S2 --cell C2 --fits-tag RMXS2d --rotation <δ> --set dev` (개발 시행 2560..3071 을 같은 δ 로 회전, CPU) → `ald.py tune --tag RMX<δ>ALD --ckpt ckpt/d2sx_S2d_N160000_a1_best.pt` (GPU; 격자·β 규칙·멈춤 규칙 = ALD16e4 §0 원문; 격자 끝이면 끝값 + 캐비엇) — **끝났고 §5 에 기록**(설계 동결 전; 개발 NMSE 만, BLER 없음). 테스트 = `regen --set test --rotation <δ>` → `estimate` (GPU float32, deterministic, TF32 꺼짐, prov). **공정성**: 조정은 baseline(ALD)에 조건 δ 를 알려주고 V1 루프는 아무것도 받지 않는다(V1 에 불리한 방향); 정적 ALD16e4 는 0° 조정이었고 ALD 대 ALD(정적) 짝은 두지 않는다. 01_RULES §9.3 GPU 예외 재적용(DECISIONS 줄). 선행 코드(§4): `ald.py --rotation`(regen; npz 에 저장, tune/estimate 가 prov 로 전파), `ald.py --train-prior`(runner 와 같은 세 조건: ckpt prior == train_prior ≠ --prior, fits full32 실경로 `fit_<train_prior>_`), runner 가 `--ald-file` 의 rotation ≠ `--rotation` 이면 실행 전 거부 |
| **실행** | ROT16e4 종료 → c-rotmix 병합(main) → 병합 diff → 산출물 이동 → `bash code/run_rotmix16e4.sh` (CPU, GPU 숨김, tmux). 태그마다 `runner.py run …` → `run_manifest.py`; `analysis` 는 (A) 만. 로그 `logs/run_rotmix16e4.log`, 끝 `ROTMIX_EVAL_DONE ok=<n> fail=<n>`. 15 태그 전부 실행·보고; 인자 부분집합은 재개 전용. **CPU 순서(사용자 순서 A→B→B′→C)**: ROTMIX(≈ 3 h) 먼저, 그 뒤 S2V(≈ 9 h) — 겹치지 않게 |
| **수용 검사 (스크립트가 한다; 명세)** | (a) 링크 전수: 태그마다 `readlink -e` 로 모든 링크가 `fit_S2d_Nr8_` 로 풀리고 `.k0r` 후보 없음, 개수 15 (k1 은 13). (b) `eval_accept.py --prior S2 --bstar kron --kron-K 4096 --ll-val -5.574511189627533 --ntrain 160000 --tag RMX<δ>:best:ceec0222e0912a1c:C2 --tag RMX<δ>PIL:best:… --tag RMX<δ>ALD:best:… --tag RMX<δ>last:last:98bc88f7333f19ee:C2 --ref-raw <δ 별 기준 raw> --fits-dir results/gmm_fits_D2_RMX<δ> --grid "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"`; k1 태그는 `--bstar kron --kron-K 1024 --ll-val -8.988496590420036 --fits-dir results/gmm_fits_D2_RMX<δ>k1 --grid "full:… kron:16,…,1024"`. (c) **적합 지문(양성)**: (A) raw 의 `meta|ll_val|gmm16..512`·`ll_val|kron` **전부**가 `gmm_fits_D2_S2dB16e4/fit_S2d_*.npz` 의 ll_val 과 같고(`ll_val|gmm32` = Chat 이 든 파일의 지문), `meta|em_sec` = 15 병합 파일 `sec` 합; 같은 δ 의 (A)(B)(C)(D) 사이 em_sec·ll_val|\* 동일. (d) **불일치 적용의 음성 검사**: δ = 0 에서 (A) 의 bstar·R2 nmse 가 `raw_B16e4k` 의 정합 arm 과 비트 동일이 **아님**(raise 없는 시행). (e) **시행 동일성 지문 둘**: R5-genie blk_err·ber·tauL_gmean·alphaD @1..16 이 δ 별 기준 raw 와 비트 동일(15 태그 전부); δ = 0 의 (A) 에서 **R3-bigamp(prior 무관)** 의 KEYS_RAW 전부가 `raw_B16e4k` 와 비트 동일. (f) `meta|rotation` = δ (모든 청크), 모든 청크가 같은 깨끗한 커밋, 시행 수 2560, 점 집합 7 SNR, load_raw 경고 없음. (g) (C): ALD 추정 파일 ckpt sha = `_best`, rotation = δ, ALD arm 예외 0, nmse@1 = 사전 계산 ĥ 오차(rtol 1e-9); (B): V1-pilot·bstar-pilot 예외 0, V1-pilot@1 = (A) V1@1 (같은 가중치). 학습 prior 의 증명 = ckpt sha(`prior='S2d'`) + (c)(d) (runner `meta|train_prior` 는 선행 코드로 추가; 있으면 함께 검사). 실패 → 그 태그 무효(판정 없음, 원인 기록, 재실행은 사용자 승인) |
| **판정 1 — 주 라벨 (표 B, D2 C2)** | **RB-15, RB-30**: `M-ours-bstar → M-ours-dscore-C-V1` (둘 다 S2d, `_best`·kron 4096, 같은 회전; (A) 안에서). 주 라벨 2 개(보정 없음). **RB-0** 는 측정 라벨(MISMATCH 형: 학습 S2d → 평가 S2). **RB (i) 는 표류 학습이 도움이 됐다는 근거가 아니다**(같은 데이터를 받은 두 prior 의 비교일 뿐); 도움 여부는 DT·DD 만 말한다 |
| **판정 2 — 표류 학습 효과 (측정 라벨, 짝 = δ 별 기준 raw)** | **DT-V1(δ)**: `V1(정적 legacy-last, 기준 raw) → V1(S2d last-EMA, RMX<δ>last)` — 역할 일치(last ↔ last); `_best` 대 정적 last 는 보고 전용. **DT-b\*(δ)**: `b*(정적 kron 1024, 기준 raw) → b*(S2d kron 1024, RMX<δ>k1)` — K 일치; kron 4096 대 정적 1024 는 보고 전용(문자열에 K 명시). δ ∈ {0, 15, 30} → 6 라벨 |
| **판정 DD — 차이의 차이 (측정 라벨, δ ∈ {15, 30}; 사용자 결정 09-27 23:2x CDT)** | **DD-δ**: ΔR_b\*(δ) = R_b\*(S2d, δ) − R_b\*(정적, δ), R = (F_b\* − F_V1)/(F_b\* − F_genie), **S2d 쪽 = (RMX<δ>: b\* kron 4096) 과 (RMX<δ>last: V1 last-EMA), 정적 쪽 = 기준 raw 의 b\* kron 1024·V1 legacy-last·genie** — 1차 −3 dB, 같은 시행 인덱스 복원추출(6 arm 동시, B = 2000, `default_rng(20260926)`) 90% CI 세 갈래: **CI > 0 "회전 δ 에서 표류 학습이 V1 의 genie 격차 회수율을 b\* 대비 높였다", CI < 0 "낮췄다", 0 포함 "판정하지 못함"**. 포화 가드(S2V §1): 두 b\* 중 하나라도 −3 dB BLER@16 ∉ [0.005, 0.9] 또는 F_b\* ≤ F_genie 면 1차 "정의하지 않음" → 2차(판정점 3 점 합, 앵커 = S2d b\*)만 보고. **비대칭 캐비엇(문장에 붙인다)**: GMM 쪽 K 가 4 배(4096 대 1024) → V1 에 **불리한** 방향; V1 은 last ↔ last 로 맞춤. DD-0 는 보고 전용(라벨 없음). 같은 K(S2d kron 1024) 로 계산한 ΔR 도 보고 전용으로 나란히 |
| **판정 3 — 등록된 baseline 전부 (측정 라벨, δ 마다)** | 𝔅 (12 개, S2V §1 과 같은 목록) = {bstar-scalar, gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, bstar-pilot, V1-pilot, ALD-pilot, ALDv-pilot} — S2d 학습·적합 또는 prior 무관. δ 마다 `X → V1(S2d _best)` 표 B; b\* 와 합쳐 13 개; "δ 에서 등록된 baseline 13 개 중 k 개에서 (i), (ii) m 개"; **X\*(δ)** = 𝔅 ∪ {b\*} 중 −3 dB 실패 최소(동률 사전순), R_{X\*} 와 CI; "전부와 멀어진다" 문장 조건 = S2V §1 과 같다(k = 13, m = 0, R_{X\*} CI 하한 > 0), δ 마다 따로. 분모 13 고정(포화 가드로 R_X 가 정의되지 않아도 표 B 라벨은 나온다) |
| **판독 — genie 격차 회수율** | δ 마다 X ∈ {b\*} ∪ 𝔅 의 R_X (S2V §1 정의·paired bootstrap·포화 가드·2차 규칙 그대로; 수치·CI 만, 대역 문장 없음), 표에 전부. 정적 학습의 R_b\*(δ) (기준 raw) 를 나란히. SNR@0.1 격차 = `analysis.gain` (seed 20260925), R = recovery (seed 20260926) |
| **다중성** | 주 라벨 2 (RB-15, RB-30) + 측정 라벨 RB-0 1, DT 6, DD 2, baseline 12 × 3 = 36 → 45; 보고 전용 pair 별도. 등록 사이 보정 없음; 1차 검정 수는 원고에 공개. 개별 (i) 을 독립 주장으로 쓰지 않는다 |
| 보고 전용 | 비교마다 SNR@0.1 격차(90% paired bootstrap), 판정점 a:b, SNR 별 실패 수(전 arm, 15 태그), 대조군 `b* → bstar-scalar`, V0·V4·V4b 행, `V1-pilot → V1`, F3 가드 발동률, `R2(정적) → R2(S2d)`, `V1(S2d _best) → V1(S2d last)`, `b*(S2d 1024) → b*(S2d 4096)`, GB′ (§5), 격자 표 (§5), ALD 조정 표 (§5) |
| 비용 (실측 기준) | CPU: (A) 14 arm ≈ 35 분 × 3 [D3B16e4 34.9 분 @ kron 4096], (B) ≈ 4 분 × 3, (C) ≈ 1 분 × 3, (D)(E) ≈ 3 분 × 6 → ≈ 2.2 h (+ 수용·짝 계산). GPU: ALD 조정 3 × ≈ 14 분(끝남), 추정 3 × < 1 분 |

## 2. 라벨 (UNDECIDED / 비유의는 "판정하지 못함")

| 표 B | RB (b\*(S2d) → V1(S2d)) | DT-V1 (V1(정적 last) → V1(S2d last)) | DT-b\* (b\*(정적 1024) → b\*(S2d 1024)) |
|---|---|---|---|
| (i) POWERED, second fewer ≥ 2/3 | "표류 학습 prior 끼리, 회전 δ 에서 V1 이 b\* 보다 적게 실패" | "회전 δ 에서 표류 학습 V1 이 정적 학습 V1 보다 적게 실패" | "회전 δ 에서 표류 학습 b\*(kron 1024) 가 정적 b\*(kron 1024) 보다 적게 실패" |
| (ii) POWERED, first fewer ≥ 2/3 | "… b\* 가 V1 보다 적게 실패" | "… 정적 학습 V1 이 적게 실패" | "… 정적 b\* 가 적게 실패" |
| (iii) / (iv) / 무효 | "판정하지 못함 (유의 방향 없음 / 검정력 미달)" / 원인 기록 | 같음 | 같음 |

| DD-δ (ΔR_b\*, −3 dB, 90% paired CI) | 기록 |
|---|---|
| CI > 0 | "회전 δ 에서 표류 학습이 V1 의 genie 격차 회수율을 b\* 대비 높였다 (GMM 쪽 K 4 배 캐비엇)" |
| CI < 0 | "… 낮췄다 (같은 캐비엇)" |
| 0 포함 / 정의하지 않음 | "판정하지 못함" / "정의하지 않음(범위 밖), 2차 값만" |

- **주 라벨 두 개의 원고 문장(미리 고정; ROT 형식)**: RB-15·RB-30 둘 다 (i) → "표류(0°~30°)로 학습한 prior 끼리 비교하면, 회전 15°·30° 모두에서 V1 이 b\* 보다 적게 실패"; 하나만 (i) → 그 각도 문장 + 다른 각도는 라벨 문자열 그대로; 둘 다 (i) 아님 → 주장 없음.
- **"V1 이 표류 학습으로 GMM 보다 더 많이 얻는다" 는 DD 라벨(CI > 0)로만, 그 문자열로만 쓴다**; DT-V1·DT-b\* 의 조합으로 만들지 않는다.
- 범위: 표류 = 수신 배열 회전 한 변수, 학습 범위가 시험 각을 포함(끝점 포함), D2 C2 한 셀, N′ = 1.6e5, 혼합 prior. "비정상 채널에 강건" 같은 일반 문장은 쓰지 않는다. 판정 3 의 "전부" 문장은 "이 셀·예산·prior·δ 와 등록된 13 개" 한정.

## 3. 미리 적는 예측 (ROT 라벨을 보기 전; 항목마다 적중/빗나감; (iv)·무효는 채점 불가, (iii) 는 "(i) 아님")

0. 이미 실현된 것(채점 안 함): 학습 patience 1368, b\* kron 4096 (연속 격자 끝, 1024→2048→4096 +2.14/+1.27 nat), ALD 조정 3 개 격자 안쪽(§5).
1. **RB-15 = (i)**, **RB-30 = (i)** (두 항목).
2. RB-0 = (i) (한 항목).
3. DT-V1(30°) = (i) (한 항목); DT-V1(0°) = (ii) 또는 (iii) (한 항목; (i) 빗나감, (iv) 채점 불가); DT-V1(15°) 예측 없음(기록만).
4. DT-b\*(30°) = (i) (한 항목); DT-b\*(0°/15°) 예측 없음.
5. **DD-30 CI > 0** (한 항목); DD-15 예측 없음.
6. 판정 3: 각 δ 에서 13 개 중 (i) ≥ 10 (δ 별 세 항목); V1-pilot 은 (iv) 또는 (iii) 가능.
7. 빗나갈 경로: RB (ii) → 그대로; genie·R3 비트 동일 실패 → 그 태그 무효; 링크 검사 실패 → 태그 무효.

## 4. 선행 작업 (갱신한다)

| 항목 | 상태 |
|---|---|
| 학습·격자·b\* (worktree `~/t2_wtB`, `logs/s2d.log`) | 완료 09-27 22:11 CDT; kron 2048·4096 병합·b\* 22:13 CDT |
| ALD δ 별 개발 조정 (GPU 3/4/5, `logs/ald_tune_RMX<δ>ALD.log`) | 완료 23:23~23:25 CDT (§5) |
| GB′ (`run_d2_sx.py --prior S2d --ntrain 160000 --tag S2dB16e4 --fallback 1`, GPU 1, tmux `s2dgb`) | 완료 09-28 00:21 CDT (§5; 이 §5 커밋) |
| **설계 동결 커밋(c-rotmix)** = 이 문서 v2 + S2V v2 + 검토 2 건 + `ald.py --rotation` + DECISIONS 줄 | 이 커밋 |
| 선행 코드(브랜치, 병합 전; 별도 커밋): `ald.py --train-prior` 가드·rotation prov 전파, runner `--ald-file` rotation 대조 + `meta\|train_prior`, `run_rotmix16e4.sh` (15 태그, 링크 생성·검사, 수용 (a)~(g)), `pair_baselines.py` (S2V 와 공용; X 별 표 B·R_X·X\*), `pair_rotmix.py` (DT·DD: 기준 raw ↔ RMX raw, 무결성 목록 §1 (c)~(g)), 스모크(`runner.py smoke … --train-prior S2d --rotation 15 --pilot-arms --tag RMXsmoke`, n = 2; 가드 4 경우: 플래그 없음 거부 / S2 가중치 + `--train-prior S2d` 거부 / 링크 없는 태그 거부 / 등록형 통과; raw 삭제) | 대기 |
| ROT 종료 → c-rotmix 병합 → 병합 diff → 산출물 이동(ckpt 2·fits 24·σ 격자·GB′·`results/ald/*RMX*`·로그; sha 재확인) → `git worktree remove ~/t2_wtB` | 대기 |
| ALD 테스트 추정 3 개 (GPU) → `run_rotmix16e4.sh` → §6 (15 pair 파일 뒤) | 대기 |

## 5. 평가 전 고정 기록

| 항목 | 값 |
|---|---|
| PID·DRIFT | PID 10, `DRIFT["S2d"]` = 30° (라디안 저장), δ 블록 공통·마지막 추출 |
| 격자 (병합 ll_val; 선택 재시작, n_iter, 재시드) | **kron**: 1024 **−8.988496590420036** (r2, 320, 315; r0 −9.0127 271/245, r1 −9.0561 309/0) / 2048 **−6.8464024185560675** (r1, 288, 1,455; r0 −6.9026 310/2,406, r2 −6.8634 251/1,984) / **4096 −5.574511189627533** (r2, 197, 46,019; r0 −5.8960 159/41,331, r1 −5.7654 182/51,113; 후보 산포 0.32 nat, `sec` 합 3769.8 s, train–val 갭 5.218). **full**: 512 −13.496468885523354 (458 iter) / **256 −14.093572211507613 (500 iter = 상한 도달, b\* 아님)** / 나머지 §C.16 (검토 파일). 1024 → 2048 → 4096 이 +2.14 / +1.27 nat 로 아직 오르는 중 = 격자 끝 캐비엇의 근거; 4096 재시드 4–5 만 회(MIX3 선례 형식) |
| 최종 b\* | **kron K = 4096, ll_val −5.574511189627533** (재시작 2), 격자 끝 → 멈춤(사용자 결정 (3)). 같은 K 대조 b\*₁₀₂₄ = kron 1024, **−8.988496590420036** |
| 체크포인트 | last **98bc88f7333f19ee** ep 1368 (patience, aborted False, fallback 1 = 클리핑 없음), best **ceec0222e0912a1c** ep 1348 = last.best_epoch ✓, best val 3.482288e-01; 둘 다 `prior='S2d'`, `sigma_tag='S2d'` (`logs/train_d2sx_S2d_N160000_a1.log`; 학습은 재부팅으로 끊겨 21:48 CDT 원자적 체크포인트에서 재개, 22:11 종료) |
| σ 격자 | `sigma_grid_D2_S2d.txt` 2026-09-28 03:45:06 KST, git 2640bb87, C1·C2; 학습 로그 σ 범위 [3.2509e-02, 8.4930e-01] = 격자 1–99 백분위 |
| **ALD δ 별 조정 (`results/ald/tune_RMX<δ>ALD.json`, 09-27 23:0x~23:25 CDT, git dca8d19c, ald.py sha 5cc14d94b32e5c9a, ckpt ceec0222e0912a1c, float32 deterministic TF32 off, seed 20260927, 개발 2560..3071)** | 세 δ 모두 c = **0.01**, β = **0.005** (β 축 두 번 확장 1e-4, 1e-5; 개발 최적 β = 1e-5 가 β = 0.005 보다 0.1 dB 이내 → 저자 기본값 유지; 격자 끝 없음). 멈춤 단계 (−3..+15): 0° 288 295 353 447 546 600 600 / 15° 289 308 359 445 546 600 600 / 30° 300 314 369 460 560 600 600. 개발 NMSE dB: 0° −6.4 −8.9 −11.7 −14.7 −18.0 −21.6 −24.4 / 15° −6.3 −9.1 −11.7 −14.7 −18.1 −21.6 −24.3 / 30° −6.5 −9.1 −11.9 −14.9 −18.2 −21.5 −24.4. v (−3..+15): 0° 0.2231 0.1222 0.0661 0.0328 0.0157 0.0067 0.0035 / 15° 0.2237 0.1177 0.0651 0.0334 0.0152 0.0067 0.0036 / 30° 0.2151 0.1169 0.0627 0.0320 0.0147 0.0067 0.0035. 캐비엇: +12/+15 dB 멈춤 600(스케줄 끝; ALD16e4 §0 과 같음) |
| GB′ (격자 확정 뒤 22:13 CDT 실행 → 00:21 CDT; last 파일 기준, run_d2_sx 관례; GPU 1) | `logs/s2d_post.log`: `GMM b* = kron (kron K=4096) @N=160000` (= §5 b*), held-out 디노이징 NMSE 비 확산/GMM **min 0.4533 · max 0.8877 · median 0.5186**, worst excess −0.112, equal_budget=True; `results/d2_gbprime_S2d_N160000_a1.npz`, `d2_gbprime_S2d.csv`. 참고(같은 척도): D3 0.559, S2v C6 0.570, D2 C2 1.6e5 헤드라인 비동일예산 0.46 |
| ROT pair 파일 수 (설계 동결 시각) | 3 (`pair_ROTaB16e4k`, `pair_ROTbB16e4k`, `pair_ROTaNR16`; 내용 미열람) |
| 설계 동결 커밋 / §5 GB′ 커밋 / 선행 코드 커밋 / 병합 커밋 / 병합 diff / 링크 mtime | **389e23f4** / [이 커밋] / [뒤] / [ROT 뒤] / [ROT 뒤] / [뒤] |

## 6. 결과 (이 절은 추가만 한다)
