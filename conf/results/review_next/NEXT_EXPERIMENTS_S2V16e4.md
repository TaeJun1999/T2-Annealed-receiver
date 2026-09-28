# NEXT_EXPERIMENTS_S2V16e4 — 공간 비정상 채널(수신 측 가시 창, S2v) C6 16×4 동일예산 N′ = 1.6e5: V1 대 b\* 와 **등록된 baseline 전부** (사전 등록 v2)

- 작성: 2026-09-27 22:39 CDT (= 09-28 12:39 KST) 초안 v1 (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 8·권고 12; `prereg_reviews_2026-09-27/review_S2V16e4.md`) 반영 v2 2026-09-27 23:18 CDT (Fable 5.1). **동결 = 브랜치 `c-rotmix`(worktree `~/t2_wtB`) 의 커밋**(이 문서 + DECISIONS 줄; ROT16e4 실행 중이라 main HEAD 를 바꾸지 않는다). 병합은 ROT 종료 뒤; 병합 뒤 `git diff <동결> <병합> --stat -- conf/code Demo` 출력을 §5 에 적는다. 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_C6B16e4.md` (C6 16×4 동일예산, UNGATED 측정, `_best` 판정 태그, 수용 검사), `NEXT_EXPERIMENTS_SVB16e4.md` (새 prior 변형의 14 arm 평가, 비짝 ΔR, 포화 가드), `NEXT_EXPERIMENTS_PILOT16e4.md`·`NEXT_EXPERIMENTS_ALD16e4.md` (파일럿 전용 arm·ALD arm — 같은 시행·같은 가중치, 무결성), `08_SPEC_analysis.md` §2 표 B, `01_RULES` §4·§5·:76·:77·§9.3.
- **작성 시점 공개**: 사용자 결정 — 비정상 실험 순서 "A(DOP) → B(ROT) → 가능하면 C(공간)" (2026-09-27 오전), C = 16×4 가시 창(09-27, worktree `~/t2_wtC` 브랜치 c-s2v, main 병합 602f8971), "C·B′ 등록은 14 arm 전부 + ALD, baseline 마다 genie 격차 회수율"(09-27 14:17 CDT), 사용자 목표 "제안 prior 가 genie 에 가깝고 **모든** baseline(GMM·학습 방법)과 멀어지게 — 사전 등록·동일 예산·감사된 방법으로만" (09-27, 09-28 재확인), 𝔅 에 V1-pilot 포함(09-27 23:1x CDT, 검토 반드시 4). 작성 시점에 본 것: 정적·PILOT·MISMATCH·ALD·SEEDS·DOP 결과. **ROT16e4 노출(사실대로)**: v1 작성 시각(22:39 CDT)에 `pair_ROTaB16e4k.txt`(18:48 CDT)·`pair_ROTbB16e4k.txt`(18:58)·`pair_ROTaNR16.txt`(21:49; 이 등록과 같은 셀 C6·같은 `_fb2_best` 가중치의 15°) 세 파일이 이미 있었다. 등록자(이 세션)는 그 파일도 `raw_ROT*`·`tables_*ROT*` 도 열지 않았고 `logs/run_rot16e4.log` 의 수용·무결성 줄(`acceptance rc=0`, `pair_rot rc=0 (# … raised {…: 0}` 머리말)만 보았다; 검토자도 존재·mtime 만 보았다. 동결 커밋 시각의 pair 파일 수는 §5 에 적는다. 증명은 없으므로 공개가 방어다. S2v 의 BLER 은 어떤 arm 으로도 실행된 적 없다(예외: σ 격자 측정, §1). 학습·GMM 격자·GB′·ALD 개발 조정은 등록 전에 끝났다(§5).
- 목적: **공간 비정상**(경로마다 수신 배열의 일부 연속 소자에만 보이는 가시 창 — XL-MIMO 가시 영역 모형의 가장 단순한 형태를 Nr = 16 에 축소한 것)에서, 같은 1.6e5 채널로 학습·적합한 V1 이 GMM b\* **및 등록된 baseline 전부** 보다 적게 실패하는지, genie 격차를 각 baseline 대비 얼마나 메우는지를 잰다. D2 S2 C6 (NR16B16e4) 와 같은 셀·예산이며 prior 만 다르다.

---

## 0. 모델과 출발점 (판정에 쓰지 않는다)

- **S2v** (`code/d2.py` `D2VisGen`, PID 9 = 새 스트림, 병합 602f8971): S2 기하(경로 수 L, AoA θ ~ U[−60°, 60°], AoD φ, 위상 ψ 를 `D2Gen._draw` 와 같은 순서로 추출)에 이어 경로마다 가시 창 폭 w ~ U{Nr/4, …, Nr} (Nr = 16 → U{4..16}), 시작 s0 ~ U{0, …, Nr − w}; 수신 응답 = VIS_NORM · mask · a_r(θ) (창 밖 소자 0), VIS_NORM = √(8/5) (E[w] = 5Nr/8 → E‖a_r‖² = 1, 교차항은 ψ 균등으로 소멸 → E‖H‖² = NrNt 해석적). "같은 rng 상태에서는 S2 의 (L, θ, φ, ψ) 를 그대로 뽑은 뒤 창을 뽑는다" 는 코드 성질이고, 학습·테스트 스트림은 PID 로 S2 와 **다르다**. 송신 측·파일럿 규칙(`make_pilots` → 송신 앙상블 Rt 만 사용) 은 S2 와 같다(C6 = `dft`). 해석적 수신 앙상블 Rr 은 S2v 에서 정의되지 않지만 어느 arm 도 쓰지 않는다(R2·GMM 의 Chat 은 학습 집합에서, `sigma.CHAT_FROM_TRAIN`).
- 모형 한계(공개): 창 폭·위치가 경로별 독립, 창 안 진폭 균일, 경계가 날카롭고, 송신 측은 불변 — 실제 가시 영역의 공간 상관·부드러운 경계는 없다. Nr = 16 은 XL 배열이 아니다.
- testbed 검사 파일은 아직 없다 — `results/testbed_S2v.txt` 는 §4 의 `code/testbed_s2v.py` 로 동결 뒤(ROT 종료 뒤 main 병합 뒤) 만든다: 정규화 E‖H‖²/(NrNt) (MC, 이전 세션 관측 1.001), 블록 안 수신 소자 전력 변동계수(관측 0.62; S2 0.39), 앙상블 Rr 대각의 퍼짐, 창 폭·시작의 경험 분포 = U{4..16}·U{0..Nr−w}; `d2.py` 의 "해석적 C_ens 대 MC" 항목은 S2v 에서 설계상 불일치이므로 "Rr 미정의" 로 표기. 이 값들은 판정과 무관하다.
- **비교 대상 D2 S2 C6 1.6e5 (NR16B16e4, `_fb2_best`)**: −3 dB 실패 b\* 184 / V1 53 / genie 22; 표 B 213:18 POWERED 3/3; 회수율 R(−3 dB) **0.809 [90% 0.747, 0.870]**. **짝 없음**(PID 4 vs 9).
- **이미 실현된 것 (등록 전 관측, BLER 아님, 채점하지 않음)**: (a) 학습 2483 epoch patience 정지(best 2463, val 0.4519517; 재부팅으로 두 세그먼트 — §5), 발산 없음 → §3d 사다리 미발동; val 이 S2 C6 (0.1785) 보다 높은 것은 데이터 분포(DSM 손실의 바닥)가 달라서다. (b) GMM b\* = kron K = 4096, 격자 끝 → 멈춤; 2048 병합 대비 **+0.061 nat 뿐**(S2 C6 는 +1.19) 이고 세 재시작 모두 train-ll 규칙 정지·검증 최고 = 마지막 평가(§5 — C6B16e4 §6.5 형 캐비엇을 **사전에** 기록). full 최고 256 (내부). (c) 동일예산 GB′ (held-out 디노이징 NMSE 비 확산/GMM b\*, σ 격자 20 점) min 0.5186 · max 0.6912 · **median 0.5699** — S2 C6 median 0.283 보다 1 에 가깝다 = 파일럿 단계에서 확산과 GMM 이 S2 보다 가깝다 → §3-1 에 **반대** 방향의 근거(확신 등급에 반영).

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산** | C6 = Nr 16, Nt 4, T 16, Tp 4, 7 SNR (−3…+15; **결과 뒤 격자를 늘리지 않는다**), n = 2560, 테스트 시행 **0..2559** (chunk 40 → {(40k, 40): k = 0..63}). N′ = 160000: 채널 집합 하나 = `arms.training_set("D2","S2v",16,4,160000)` (스트림 7) 를 GMM 적합과 score 학습(자체 9:1 = 144000/16000, split_hash a2d75bb465dc9147)이 함께 쓴다; GMM 검증 5000 = 스트림 8. **예외(공개)**: σ 격자 측정(`sigma_grid_D2_S2vNR16`)이 C6 테스트 시행 0..63 을 Gaussian 수신기(M-ours-G 인터페이스)로 한 번 실행했다 — ν_q 만 기록, BLER 없음, 헤드라인·D3·SV8e 관례와 같음 |
| **지위** | **UNGATED** (C6·SV8e 선례; D1 형제 없음) → **"공간 비정상 축의 측정"** 이며 arm 판정이 아니다. 헤드라인(C2 1.6e5 B16e4k) 불변; S2v 는 어느 결과에서도 헤드라인이 되지 않는다 |
| **GMM 격자와 b\*** | 기본 격자 full K ∈ {16..512} (κ ∈ {0,16,64,256} × 재시작 3, 정확 경로), kron K ∈ {16..2048} (κ = 0, 재시작 3); 선택 = validation ll 최대(`arms.gmm_selection`). 반복 규칙(B32e4 §1): b\* 가 그 계열 최대 K 이면 2K, **kron 4096 에서 멈춤 + 격자 끝 캐비엇**(사용자 결정 09-26 (3)); full 512 가 b\* 이면 full 1024 한 번. **적용 결과(§5)**: b\* = kron K = 4096, ll_val **−58.45384925132457**, 격자 끝 → 멈춤; full 최고 256 (내부) → full 1024 규칙 미발동. kron ≤ 512 는 배치 경로(kron 512 = 배치 재시작 3 개 병합, DECISIONS 09-28 11:38 KST; 배치 kron M-step 은 Nr=16 K ≤ 512 에서 검증), kron ≥ 1024 재시작별 후보 → CPU 병합. BLER 은 선택에 쓰지 않는다 |
| **체크포인트·평가 가중치** | 동결 레시피 `train_nr16.py --prior S2v --sigma-tag S2vNR16 --ntrain 160000`, rung D2SXS2vNR16160000 attempt 1(시행 1, 클리핑 없음). **측정 판정 태그 `S2vB16e4` = `ckpt/d2sx_S2vNR16_N160000_a1_best.pt`** (sha256[:16] fef34e13133004fc, epoch 2463); **`S2vB16e4last` = `…_a1.pt`** (9940812e5f7ab689, epoch 2483, last-EMA) 보고 전용 |
| **σ 격자** | `results/sigma_grid_D2_S2vNR16.{txt,npz}` (09-28 01:33:48 KST = 09-27 11:33 CDT, git 063f3bcb, C6, n = 64, Gaussian 수신기): 20 점 σ ∈ [3.2660e-02, 4.9941e-01] — 학습 로그 머리말과 일치. S2 C6 는 1e4 적합의 `NR16` 격자([3.283e-02, 4.915e-01])를 재사용했으므로 두 학습의 잡음 범위는 같지 않다(ΔR 행) |
| **arm (4 개 실행 태그, 같은 시행; 실행 순서 ① → ③ → ④ → ②)** | ① `S2vB16e4` (`_best`): 14 arm = M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32, M-ours-dscore-C-V0/V1/V4/V4b, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, R5-genie. ③ `S2vPIL` (`_best`): `--pilot-arms --arm V1-pilot bstar-pilot R5-genie` (PILOT16e4 §1 정의; fits 링크 `gmm_fits_D2_S2vPIL → gmm_fits_D2_S2vB16e4`). ④ `S2vALD` (`_best`): `--ald-file results/ald/ald_S2vALD.npz --arm ALD-pilot ALDv-pilot R5-genie` (ALD16e4 §1 정의; 링크 `gmm_fits_D2_S2vALD`). ② `S2vB16e4last` (last-EMA): 같은 14 arm, 보고 전용, 맨 뒤(링크 `gmm_fits_D2_S2vB16e4last`). ②③④ 의 genie 는 ① 과 비트 동일해야 한다(같은 시행 = 짝의 전제). ① 이 ABORT 이면 ②③④ 를 시작하지 않는다(참조 없음) |
| **ALD 사전 계산 (ALD16e4 §0·§1 절차 그대로; 조건 열거)** | 저자 코드 갱신식, 네트워크 = ① 의 `_best`, L = 200 기하 레벨 × M = 3, 무작위 초기값 CN(0, I), c 격자 {1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1} × β {0.001, 0.005, 0.01, 0.1, 1} + 격자 끝 확장 ≤ 2 회, β 규칙(개발 최적이 β = 0.005 를 0.1 dB 넘게 이기지 않으면 0.005), 멈춤 단계 = SNR 별 개발 평균 NMSE 최소(1..600), ALDv 의 v = 그 단계의 개발 MSE/원소. **조정은 개발 시행**(SNR 별 trial `C.DEV_SKIP0` = 2560.. +512, `ald.py regen --set dev`)의 **NMSE 만** 보고 **동결 전에** 끝내 §5 에 기록한다(`results/ald/tune_S2vALD.json`; BLER 없음). 테스트 추정: `ald.py regen --tag S2vALD --prior S2v --cell C6 --fits-tag S2vB16e4 --set test` (CPU, GPU 숨김) → `ald.py estimate --tag S2vALD --ckpt ckpt/d2sx_S2vNR16_N160000_a1_best.pt --set test` (GPU float32; `torch.use_deterministic_algorithms(True)`, TF32 꺼짐, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, 추정 파일에 prov = ckpt sha·ald.py sha·git·GPU·정밀도, 첫 SNR 두 번 계산 비트 동일 assert; 조정 기록보다 오래된 추정 파일은 재계산). **01_RULES §9.3 의 GPU 예외(추정기 사전 계산만)를 이 등록에 같은 조건으로 재적용**(DECISIONS 동결 줄). 수신기는 CPU complex128 |
| **실행 (명령 원문)** | ROT16e4 종료 → c-rotmix 병합 → §5 병합 diff 확인 뒤, `bash code/run_s2v16e4_eval.sh` (선행 코드 §4; tmux, CPU 192 워커, GPU 숨김). 태그마다 `runner.py run --testbed D2 --prior S2v --cell C6 --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/<가중치> --tag <태그> [arm 옵션]` (16 반복, `arms.LOOP` 그대로) → `run_manifest.py --tag <태그>`; `runner.py analysis` 는 **①② 만**(③④ 는 3 arm raw 라 표 A 가 죽는다 — PILOT §1 선례); `guard_report.py` ①②. 수용: `eval_accept.py --prior S2v --nr 16 --bstar kron --kron-K 4096 --ntrain 160000 --ll-val -58.45384925132457 --tag S2vB16e4:best:fef34e13133004fc:C6 --tag S2vB16e4last:last:9940812e5f7ab689:C6 --tag S2vPIL:best:fef34e13133004fc:C6 --tag S2vALD:best:fef34e13133004fc:C6 --ref-raw raw_S2vB16e4 --fits-dir results/gmm_fits_D2_S2vB16e4 --grid "full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"` (`--ref-arms R5-genie` 기본 = 4 키; ② 에는 `--ref-arms all` 로 비-Stage-C 10 arm 비트 동일도 확인). 판독: `recovery_ci.py --raw raw_S2vB16e4 --cell C6 --snrs -3` (+ 판정점; last 도), `frontier_ci.py --recovery "raw_S2vB16e4:C6:-3" "raw_NR16B16e4:C6:-3"` (best; last 도 한 줄), `pair_baselines.py`(§4; X ∈ 𝔅 의 표 B·R_X). 로그 `logs/run_s2v16e4_eval.log`, 끝 `S2V_EVAL_DONE ok=<n> fail=<n>`. **§5 가 채워진 이 문서가 동결·병합된 뒤에만 시작** |
| **수용 검사** | (a) 격자 완전성(스크립트): full 6 + kron {16..4096} 9 병합 파일, K ≥ 1024 후보 `.k0r{0,1,2}` 3 개; K = 512 후보 3 개는 §5 에 파일명·ll_val 로 기록(스크립트 검사 범위 밖); (b) 태그마다 7 SNR × 청크 {(40k, 40)}, meta `ntrain=160000`, `bstar=kron`, `kron_K=4096`, `ll_val\|kron` (\|Δ\| ≤ 1e-9), ①② 의 (bstar, kron_K, em_sec) 동일(③④ 는 meta 에 있는 범위에서 — 스크립트 작성 시 확인·기록); (c) `stagec_ckpt_id` sha·role, best.epoch (2463) == last.best_epoch; (d) **R5-genie blk_err·ber·tauL_gmean·alphaD @1..16 이 ②③④ 에서 ① 과 비트 동일**; (e) GB′ 로그 `GMM b* = kron (kron K=4096)` 이 §5 와 같고 격자 확정 뒤 계산; (f) raw 파일명·analysis 머리말에 `S2v`, `cell C6 (16x4, T=16, Tp=4, …)`; (g) ④: `pair_baselines.py` 가 ALD 추정 파일의 ckpt sha = ① `_best`, 시행 수 2560, ALD arm 예외 0, nmse@1 = 사전 계산 ĥ 오차(rtol 1e-9) 를 검사(ALD16e4 (b)); ③: V1-pilot·bstar-pilot 예외 0. 어긋나면 그 태그 무효 → 원인 기록, 재실행은 사용자 승인 |
| **판정 1 — 주 측정 (표 B, C6, 태그 ①)** | `M-ours-bstar → M-ours-dscore-C-V1`: 판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR (자동), 점마다 exact 양측 부호검정. **(i) = POWERED 이고 second arm fewer ≥ 2/3.** `significant` 토큰은 기준이 아니다 |
| **판정 2 — 등록된 baseline 전부 (표 B, 측정 라벨)** | baseline 집합 **𝔅 (12 개, 여기서 고정)** = {M-ours-bstar-scalar, M-ours-gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, bstar-pilot, **V1-pilot**, ALD-pilot, ALDv-pilot}. V1-pilot 은 PILOT16e4 의 "Arvinte–Tamir 형 설정"(학습 prior 를 파일럿에서 한 번) 이라 외부 방법의 설정으로 넣는다(사용자 결정 09-27 23:1x CDT; 해석 한계 = Module H 16 회 대 1 회, PILOT §2 — 그대로 옮긴다). **V0·V4·V4b 는 V1 의 site 형식 ablation** 이라 𝔅 에 넣지 않는다(보고 전용). 각 X ∈ 𝔅 에 `X → M-ours-dscore-C-V1` 표 B (판정점 = 앵커 X 기준 자동; ③④ 의 arm 은 ① 의 V1 과 시행 인덱스로 짝 — genie 비트 동일이 전제). 라벨은 X 마다 (i)~(iv); b\* (판정 1) 와 합쳐 **13 개**. 보고 문장은 개수: "등록된 baseline 13 개 중 k 개에서 (i), (ii) m 개, 판정 못함 13 − k − m 개" + 13 개 X 별 라벨·R_X 표(골라 적지 않는다). 다중성: 13 개 비교 사이 보정 없음 — 개별 (i) 을 "V1 이 X 를 이긴다" 는 독립 주장으로 쓰지 않는다 |
| **가장 가까운 baseline X\* (결정적 규칙, 결과 전에 고정)** | **X\* = 𝔅 ∪ {b\*} 중 −3 dB 실패 수 최소인 arm**(동률이면 arm 이름의 사전순). R_{X\*}(−3 dB) 와 90% paired CI 를 "가장 가까운 baseline 대비 회수율" 로 보고한다. **원고의 "등록된 baseline 전부와 멀어진다" 문장은 k = 13 이고 (ii) 가 0 이고 R_{X\*}(−3 dB) 의 CI 하한 > 0 일 때만 쓴다**; 하나라도 어긋나면 개수 문장만 |
| **판독 — genie 격차 회수율 (X 마다; 수치·CI 만, 대역 없음)** | X ∈ {b\*} ∪ 𝔅 마다 R_X = (F_X − F_V1)/(F_X − F_genie) (F = 실패 수), 1차 −3 dB, 2차 X 의 판정점 합(판정점이 3 개 미만이면 있는 점의 합과 점 수를 표기, 0 개면 정의하지 않음), **세 arm 을 묶은 paired bootstrap** (시행 인덱스 복원추출 B = 2000, `default_rng(20260926)`, 백분위 5/95 → 90% CI; `recovery_ci.py` 와 같은 계산). **포화 가드**: X 의 −3 dB BLER@16 이 [0.005, 0.9] 밖이거나 F_X ≤ F_genie → 그 X 의 1차 R 은 "정의하지 않음(범위 밖)", 2차만. 복제에서 F_X − F_genie ≤ 0 은 제외·개수 기록, 5% 초과면 "정의 불가". **C6B16e4 의 회수율 대역 문장은 쓰지 않는다**(그 문장은 "1e4 효과가 소예산 효과인가" 전용; S2v 에는 대상이 없다 — 검토 반드시 3, 택일 (a)). b\* 의 R 은 ΔR 세 갈래 문장으로만 서술 |
| **판독 — ΔR (S2 C6 와 비짝)** | ΔR = R_b\*(S2v, −3 dB) − R_b\*(S2 C6 NR16B16e4, −3 dB = 0.809); 두 raw 독립 복원추출(B = 2000, 같은 시드; `frontier_ci.py --recovery`) 90% CI 세 갈래: CI < 0 "S2v 의 genie 격차 회수율이 S2 C6 보다 낮다", > 0 "높다", 0 포함 "판정 못함". 포화 가드 위와 같다. **비대칭(미리 공개; ΔR 문장은 채널 + 아래 학습 조건 차이의 합)**: (a) S2 C6 의 V1 은 §3d 시행 2(기울기 클리핑 1.0) 가중치, S2v 는 시행 1; (b) σ 격자 재사용(NR16) 대 자체 측정(S2vNR16); (c) 두 b\* 의 수렴 캐비엇은 방향이 같고 정도가 다르다(+1.19 vs +0.061 nat). 시드 표기: SNR@0.1 격차 = `analysis.gain` (seed 20260925), R = recovery (seed 20260926) |
| 보고 전용 | −3 dB 실패 수·BLER (전 arm), SNR@0.1 격차(90% paired bootstrap; 격자 밖이면 "n/a"), 대조군 `M-ours-bstar → M-ours-bstar-scalar`, V0·V4·V4b 표 B 행, F3 가드 발동률(전 arm), best 대 last V1 짝 부호검정, GB′ (§5; S2 C6 0.283 과 나란히), 격자 표(§5), ALD 개발 조정 표(§5), 채널 추정 NMSE@16 중앙값(arm 별), R4-llr 의 BLER@16 > BLER@1 특성(S2 C6 관측; 앵커 규칙은 BLER@16, 바꾸지 않음) |
| 비용·일정 | CPU (tmux, ROT 종료 뒤 CPU 단독, GPU 숨김): ① ≈ 4–4.5 h [추정: NR16B16e4 ① 4.1 h @ kron 4096], ③ ≈ 10 분, ④ ≈ 5 분 [PILNR16 8 분, ALDNR16 2 분], ② ≈ 4–4.5 h → 합 ≈ 9 h; 다른 CPU 작업(B′ BLER 등)과 겹치면 2 배까지. GPU: ALD 조정 ≈ 15 분(끝남), 추정 < 1 분 |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다. UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

| 판정 1 표 B `b* → V1` (C6, S2vB16e4) | 기록 |
|---|---|
| (i) POWERED, second arm fewer ≥ 2/3 | "공간 비정상(가시 창) S2v 에서 V1 이 b\* 보다 적게 실패 (측정, UNGATED)" — **R_b\*(수치·CI)·ΔR 세 갈래 문장과 반드시 함께** |
| (ii) POWERED, first arm fewer ≥ 2/3 | "S2v 에서 b\* 가 V1 보다 적게 실패" — R_b\*·ΔR 문장과 함께 |
| (iii) | "판정하지 못함 (유의 방향 없음)" |
| (iv) UNDECIDED | "판정하지 못함 (검정력 미달)" — SNR 격자 확장 없음 |
| 무효 | 판정 없음, 원인 기록 |

| 판정 2 (𝔅 12 개 + b\* = 13) | 기록 |
|---|---|
| 개수 문장 | "S2v C6 에서 등록된 baseline 13 개 중 k 개에 대해 V1 이 적게 실패 (표 B (i)); (ii) m 개; 판정 못함 13 − k − m 개" + X 별 라벨·R_X 표 + X\* 와 R_{X\*} |
| (iv) 인 X | "멀어졌다" 도 "가깝다" 도 아니다 — k 에 세지 않고 13 − k − m 에 든다 |
| "등록된 baseline 전부와 멀어진다" 문장 | **k = 13 이고 m = 0 이고 R_{X\*}(−3 dB) CI 하한 > 0** 일 때만; 그 말은 **이 셀·예산·prior 와 등록된 13 개에 한정** |
| (ii) 가 하나라도 있음 | "전부" 문장 금지; 개수 문장과 그 X 를 이름으로 |

- 원고 문장 범위: "공간 비정상 채널 일반" 이 아니라 "이 가시 창 모형·C6·N′ = 1.6e5". 어느 결과도 헤드라인·다른 등록의 라벨을 바꾸지 않는다.

## 3. 미리 적는 예측 (정적·DOP 결과와 §0 의 사전 실현 값을 본 뒤, ROT 라벨은 보기 전; 항목마다 적중/빗나감, (iii)/(iv) 는 "(i) 아님" 으로 센다)

0. 이미 실현된 것(채점 안 함): GB′ median 0.5699 (S2 C6 0.283 보다 1 에 가깝다 → 예측 1 에 반대 방향 근거), b\* kron 4096 격자 끝(+0.061 nat), 발산 없음 patience 2483.
1. **판정 1 = (i)**. 근거: C6 S2 213:18 선례; 창 폭·시작 두 이산 잠재가 경로마다 더해져 조건부 Gaussian 구조가 더 깨진다(05_SPEC 의 D2 정의 확장). **확신 중간**(GB′ 가 반대 방향). 판정점 −3/0/+3 (채점 항목).
2a. R_b\*(−3 dB) 점추정 **0.60–0.85**. 2b. ΔR 90% CI 는 0 을 걸친다 [확신 낮음].
3. 판정 2: 13 개 중 (i) **≥ 10**. X 별: R0·R1·R3·R4-llr·R4-scvamp·bstar-pilot·ALD·ALDv = (i) (8 개 묶어 한 항목: 8 개 전부 (i)); gmm32·bstar-scalar·R2 중 (i) 아님 ≤ 1 (한 항목); **V1-pilot = (iv) 또는 (iii)** (C6 S2 에서 (iv); 한 항목).
4. X\* = ALDv-pilot 또는 V1-pilot (한 항목; 둘 중 하나면 적중); R_{X\*}(−3 dB) 0.3–0.8 (한 항목).
5. genie −3 dB 실패 10–60 (S2 C6 22; 다른 스트림·채널 — 난이도 눈금; 한 항목).
6. 빗나갈 경로: (a) (ii)/(iii) → 그대로; (b) 저-BLER 로 (iv) → 격자 확장 없음; (c) ALD 조정에서 c 가 확장 끝까지 격자 끝 → 끝값 그대로 쓰고 §5 에 캐비엇; (d) k < 13 → 개수 문장만.

## 4. 선행 작업 (갱신한다)

| 항목 | 상태 |
|---|---|
| 학습(worktree `~/t2_wtC`, 09-27 11:34 CDT 시작, 재부팅 뒤 21:49 재개, 22:05 종료), GMM 격자, 큐 끝 22:15, kron 512 병합·b\* 22:16 CDT | 완료 (`logs/s2v.log`) |
| GB′ (`train_nr16.py --prior S2v --sigma-tag S2vNR16 --ntrain 160000 --fits-tag S2vB16e4`, GPU 0) | 완료 22:16~22:46 CDT (§5) |
| ALD 개발 조정 (worktree, GPU 2, `logs/ald_tune_S2vALD.log`) | 완료 23:24 CDT (§5) |
| 적대적 검토(Fable 서브에이전트) → v2 → §5 채움 → **동결 커밋(c-rotmix)** | 이 커밋 |
| ROT 종료 → c-rotmix 병합 → 병합 diff → worktree 산출물 이동(ckpt 2·fits 28·σ 격자·GB′ npz·로그; sha 재확인) → `git worktree remove ~/t2_wtC` | 대기 |
| **[09-28 00:51 CDT 완료 — c-rotmix 커밋, testbed_s2v.py 는 BLER 중 작성]** 선행 코드(브랜치, 병합 뒤 실행): `code/run_s2v16e4_eval.sh` (C6, ①③④② 순, 수용·판독 명령 §1), `code/pair_baselines.py` (X ∈ 𝔅 의 표 B·R_X paired bootstrap; 다른 raw 의 arm 을 시행 인덱스로 짝, genie 4 키 비트 동일 전제 검사, ALD·pilot 예외 0·nmse@1 검사, X\* 규칙), `code/testbed_s2v.py`, fits 링크 3 개 | 대기 |
| ALD 테스트 추정(regen test → estimate, GPU) | 병합 뒤, ④ 직전 |

## 5. 평가 전 고정 기록

| 항목 | 값 |
|---|---|
| PID·생성기 상수 | PID 9 (`common.py`), `D2VisGen`: wmin = Nr/4 = 4, w ~ U{4..16}, s0 ~ U{0..Nr−w}, VIS_NORM = √(8/5) |
| 격자 (병합 ll_val; 선택 재시작, n_iter/best@, 재시드) | **kron** (κ = 0, 재시작 3, 배치 경로): 16 −96.268 (r2, 245/210, 0) / 32 −89.663 (r2, 161/120, 0) / 64 −82.568 (r2, 191/150, 0) / 128 −76.353 (r2, 151/110, 0) / 256 −69.662 (r1, 261/220, 0) / **512 −63.337** (r0, 461/420, 0; 후보 r1 −63.634 500/490 상한 도달, r2 −63.459 371/330; `fit_S2v_Nr16_kronK512_n160000.k0r{0,1,2}.npz`) / 1024 −59.744 (r1, 453/450, 0; r0 −60.398 411/370, r2 −60.342 500/460 상한) / 2048 −58.515 (r2, 141/100, 124; r0 −59.013 301/290, r1 −58.520 231/190) / **4096 −58.45384925132457** (r0, 120/110, 5210; r1 −59.063 127/120, 5978; r2 −58.698 98/90, 5368). **full** (κ ∈ {0,16,64,256} × 3, 전부 κ = 0 선택, 정확 경로): 16 −96.409 (r2, 291/250) / 32 −89.296 (r1, 381/340) / 64 −81.747 (r0, 381/340) / 128 −77.708 (r0, 458/450) / **256 −76.513** (r2, 333/330) / 512 −80.683 (r2, 160/150, 재시드 636). 상한 500 도달: kron 512 r1·1024 r2 (후보) 뿐. kron 512 비배치(재부팅 전 GPU 0) 부분 결과는 파일로 남지 않았고 쓰지 않는다 |
| 최종 b\*, 격자 끝 캐비엇 (사전 기록) | **b\* = kron K = 4096, ll_val −58.45384925132457** (재시작 0). 격자 끝 → 멈춤(사용자 결정 (3)). **캐비엇**: 2048 병합 대비 +0.061 nat 뿐(격자 꼭대기가 평평 — "아직 오르는 중" 이라기보다 2048 과 구분되지 않음); kron 4096 세 재시작 모두 학습 우도 규칙(`ll[-1] − ll[-2] < tol·|ll|`, 재시드 수천 회)으로 멈췄고 검증 최고 = 마지막 평가 시점(it_best = n_iter − 7..10) — C6B16e4 §6.5 형 캐비엇을 여기서는 **사전에** 적는다(kron 2048 r2 도 같은 방식, 141/100). full 최고 256 은 b\* 보다 18.1 nat 낮다 |
| 체크포인트 | last `d2sx_S2vNR16_N160000_a1.pt` sha256[:16] **9940812e5f7ab689**, epoch 2483, best_epoch 2463, stopped_by patience, aborted False; best `…_a1_best.pt` **fef34e13133004fc**, epoch 2463 = last.best_epoch ✓, best val 4.519517e-01. **학습은 두 세그먼트**: 09-28 01:34:34 KST (= 09-27 11:34 CDT) 시작 → epoch 1..2403 (재부팅 전 best @2394, 0.4521922) → 서버 재부팅 → 11:49:00 KST (21:49 CDT) 원자적 체크포인트에서 재개(hp·optimizer·EMA·RNG 상태 복원, `score.train` resume 로직) → epoch 2404..2483 patience (wall 1002 s); 최종 best 2463 은 재개 세그먼트 안(차 2.4e-4). 세 번째 머리말 12:16:49 KST 는 GB′ 호출의 무동작 재개(`# resume: … no epoch trained`). 재개는 CLAUDE.md 규칙 안이며 연속 실행과 같게 설계돼 있지만 사실로 적는다 (`logs/train_d2sx_S2vNR16_N160000_a1.log`) |
| σ 격자 | `sigma_grid_D2_S2vNR16.txt` 2026-09-28 01:33:48 KST, git 063f3bcb, 20 점 [3.2660e-02, 4.9941e-01] = 학습 로그 머리말 |
| GB′ (격자 확정 뒤 실행본; last 파일 기준, run_d2_sx/train_nr16 관례) | `logs/s2v_gb.log` 22:16~22:46 CDT: `GMM b* = kron (kron K=4096) @N=160000`, GPU GMM 대 CPU 루프 상대차 8.31e-15, 비 min 0.5186 · max 0.6912 · median 0.5699, worst excess −0.309, equal_budget=True; `results/d2_gbprime_S2vNR16_N160000_a1.npz` |
| ALD 개발 조정 (`results/ald/tune_S2vALD.json`, 09-27 22:5x~23:24 CDT, GPU 2, git 9c0ca1f4, ald.py sha 865261522ca7eade, ckpt fef34e13133004fc, float32 deterministic TF32 off, seed 20260927, 개발 2560..3071) | c = **0.03**, β = **0.005** (β 축 두 번 확장 1e-4, 1e-5; 개발 최적 c=0.03, β=1e-5 −14.294 dB 가 β=0.005 의 −14.276 dB 보다 0.1 dB 이내 → 저자 기본값 유지; 격자 끝 없음). σ 범위 [0.03266, 0.49941]. 멈춤 단계 (−3..+15): 125 127 194 289 378 501 580. 개발 NMSE dB: −5.9 −8.5 −11.2 −14.3 −17.1 −20.2 −22.8. v: 0.2448 0.1282 0.0702 0.0349 0.0179 0.0090 0.0049. 캐비엇: 멈춤 600 인 SNR 없음(S2 C6 은 +12/+15 에서 600) |
| ROT pair 파일 수 (동결 커밋 시각) | 3 (`pair_ROTaB16e4k`, `pair_ROTbB16e4k`, `pair_ROTaNR16`; 내용 미열람) |
| 동결 커밋 / 병합 커밋 / 병합 diff | **389e23f4** (설계 동결) / **22370276** (`git merge c-rotmix`, 2026-09-28 02:08 CDT, 야간 체인 — BLER 시작 전) / `git diff 389e23f4 22370276 --stat -- conf/code Demo` = 7 파일 +592 −9, 전부 §4 선행 코드(b233c3a2·bcc80d3b; `after_rot_chain.log`) |
| 선행 코드 커밋, 링크 생성 시각 | b233c3a2 (pair_baselines·run_s2v16e4_eval·ald.py·runner), bcc80d3b (testbed_s2v, `results/testbed_S2v.txt`); 링크 `gmm_fits_D2_S2v{B16e4last,PIL,ALD} → gmm_fits_D2_S2vB16e4` 는 `run_s2v16e4_eval.sh` phase 0 이 09-28 04:34 CDT 생성 |

## 6. 결과 (이 절은 추가만 한다)

### 6.1 결과 (기록 2026-09-28 16:06 CDT, Opus 5.5 — 전사만, 해석 없음; 원본 `results/review_next/pairB_S2vB16e4.txt`, `recovery_S2vB16e4{,last}.txt`, `recovery_diff_S2vB16e4.txt`, `S2vB16e4_accept.txt`, `results/tables_D2_S2vB16e4.txt`, `results/guard_D2_S2vB16e4.txt`, `run_manifest_S2v*.json`)

**실행·수용**: 야간 무인 체인이 B′ 뒤 `bash code/run_s2v16e4_eval.sh` 2026-09-28 04:34 ~ 13:48 CDT (git 22370276 = 병합, §5). phase 0: 링크 3 개, ALD 테스트 파일럿 재생성(CPU) + 추정(GPU, float32 결정론). ① S2vB16e4 04:36 ~ 09:05, ③ S2vPIL ~ 09:13, ④ S2vALD ~ 09:14, ② S2vB16e4last ~ 13:43 CDT, 끝 `S2V_EVAL_DONE ok=1 fail=0`. eval_accept (네 태그, 격자 full 6 + kron 9·K ≥ 1024 후보 3 개, ckpt id, genie 재생 대조 vs ①) **ACCEPT: OK**; ② 대 ① `--ref-arms all` 은 문자 그대로 `ACCEPT: FAILED` 를 출력한다 — 다른 arm = M-ours-dscore-C-V0/V1/V4/V4b 뿐(가중치가 다르므로 등록 §1 이 예정한 차이); 비-Stage-C 10 arm 은 비트 동일이며, 이 판독은 `run_s2v16e4_eval.sh` 의 필터("non-Stage-C arms differing: none")와 기록 감사의 독립 재계산으로 확인 [기록 감사 표현 정정]. pair_baselines 무결성(점 집합, 한 개의 깨끗한 커밋, genie 4 키 ③④ = ①, raised 0, V1-pilot@1 = V1@1·bstar-pilot@1 = b\*@1, ALD 추정 고정·사전 계산값, ALD ckpt = ① `_best`) **OK**. 판정점(앵커 b\*, ①) −3/+0/+3.

**판정 1 (표 B `M-ours-bstar → M-ours-dscore-C-V1`, C6, S2vB16e4)**: −3 dB 133:25 · +0 dB 48:2 · +3 dB 21:5, pooled 202:32; POWERED; second arm fewer 3/3, first arm fewer 0/3 → **(i) "공간 비정상(가시 창) S2v 에서 V1 이 b\* 보다 적게 실패 (측정, UNGATED)"**. SNR@0.1 격차 n/a (≤ −3 vs ≤ −3; 격자 확장 없음).
- **R_b\*** (−3 dB, 1차) **0.603 [90% 0.523, 0.675]** (b\* 202, V1 94, genie 23); 2차(판정점 합) 0.646 [0.581, 0.704]. last-EMA: 0.564 [0.483, 0.640] / 0.612 [0.550, 0.671].
- **ΔR** = R_b\*(S2v) − R_b\*(S2 C6 NR16B16e4 = 0.809) = **−0.205 [90% 비짝 −0.303, −0.110] → CI < 0 "S2v 의 genie 격차 회수율이 S2 C6 보다 낮다"** (§1 비대칭 (a)(b)(c) 를 포함한 채널 + 학습 조건 차이의 합). last-EMA: −0.244 [−0.343, −0.148].

**판정 2 (등록된 baseline 13 개 = 𝔅 12 + b\*; `X → V1`)**: **(i) 13, (ii) 0, 판정 못함 0** → "S2v C6 에서 등록된 baseline 13 개 중 13 개에 대해 V1 이 적게 실패 (표 B (i)); (ii) 0 개; 판정 못함 0 개". **X\*** (−3 dB 실패 최소) = **V1-pilot** (F 152), **R_X\* 0.450 [90% 0.356, 0.536]** → 문장 조건(k = 13, (ii) = 0, R_X\* CI 하한 > 0) **충족**: "등록된 baseline 전부와 멀어진다" 를 이 셀(C6)·예산(N′ = 1.6e5)·prior(S2v 가시 창 모형)와 등록된 13 개에 한정해 쓸 수 있다.

| X → V1 | 판정점 | a:b | pooled | 라벨 | R_X −3 dB [90%] | R_X 판정점 합 [90%] |
|---|---|---|---|---|---|---|
| M-ours-bstar | −3/+0/+3 | 133:25 · 48:2 · 21:5 | 202:32 | (i) 3/3 | 0.603 [0.523, 0.675] | 0.646 [0.581, 0.704] |
| M-ours-bstar-scalar | −3/+0/+3 | 152:25 · 54:4 · 27:5 | 233:34 | (i) 3/3 | 0.641 [0.569, 0.706] | 0.682 [0.623, 0.737] |
| M-ours-gmm32 | −3/+0/+3 | 149:25 · 60:7 · 31:3 | 240:35 | (i) 3/3 | 0.636 [0.560, 0.703] | 0.688 [0.630, 0.742] |
| R0-pilot (@16) | −3/+0/+3 | 382:9 · 131:3 · 67:3 | 580:15 | (i) 3/3 | 0.840 [0.807, 0.870] | 0.859 [0.833, 0.883] |
| R1-turbo | −3/+0/+3 | 686:4 · 289:0 · 126:2 | 1101:6 | (i) 3/3 | 0.906 [0.886, 0.924] | 0.922 [0.908, 0.935] |
| R2-ours-G | −3/+0/+3 | 250:11 · 108:1 · 51:3 | 409:15 | (i) 3/3 | 0.771 [0.726, 0.814] | 0.809 [0.774, 0.841] |
| R3-bigamp | +3/+9/+12 | 228:1 · 152:1 · 190:0 | 570:2 | (i) 3/3 | 0.941 [0.929, 0.953] | 0.981 [0.969, 0.992] |
| R4-llr | +9/+12/+15 | 284:1 · 224:0 · 167:0 | 675:1 | (i) 3/3 | 0.967 [0.960, 0.973] | 0.996 [0.990, 1.000] |
| R4-scvamp | +0/+3/+6 | 399:0 · 206:2 · 116:1 | 721:3 | (i) 3/3 | 0.922 [0.906, 0.937] | 0.966 [0.953, 0.979] |
| bstar-pilot | −3/+0/+3 | 205:12 · 68:3 · 31:7 | 304:22 | (i) 3/3 | 0.731 [0.679, 0.779] | 0.752 [0.708, 0.793] |
| V1-pilot | −3/+0/+3 | 73:15 · 16:2 · 7:1 | 96:18 | (i) 2/3 | 0.450 [0.356, 0.536] | 0.456 [0.376, 0.533] |
| ALD-pilot | −3/+0/+3 | 284:19 · 119:1 · 57:3 | 460:23 | (i) 3/3 | 0.789 [0.745, 0.828] | 0.825 [0.792, 0.854] |
| ALDv-pilot | −3/+0/+3 | 255:17 · 75:3 · 37:3 | 367:23 | (i) 3/3 | 0.770 [0.724, 0.813] | 0.787 [0.748, 0.823] |

SNR@0.1 격차(보고): b\*·b\*-scalar·gmm32·V1-pilot n/a (≤ −3 vs ≤ −3); R0 ≥ +1.60, R1 ≥ +3.72, R2 ≥ +0.84, R3 ≥ +5.77, R4-llr ≥ +13.47, R4-scvamp ≥ +5.25, bstar-pilot ≥ +0.29, ALD ≥ +1.09, ALDv ≥ +0.62 dB (V1 이 격자 최저 SNR 에서 이미 < 0.1).

**보고 전용**: −3 dB BLER@16 실패 수 / 2560 — genie 23, V1 94 (last 101), V4 93, V4b 116, V0 2158, b\* 202, b\*-scalar 221, gmm32 218, R0 467, R1 776, R2 333, R3 1228, R4-llr 2180, R4-scvamp 930, bstar-pilot 287, V1-pilot 152, ALD 359, ALDv 332. 대조군 `M-ours-bstar → M-ours-bstar-scalar` 44:63 · 16:20 · 5:11, pooled 65:94, POWERED, 어느 쪽도 유의 점 없음 → (iii). `b* → V4` 133:24 · 49:4 · 21:5 (i) 3/3; `b* → V4b` 119:33 · 47:7 · 22:5 (i) 3/3; `b* → V0` 5:1961 · 1:1925 · 0:1671 (b\* 가 적게 실패 3/3). best 대 last V1 짝 부호검정 (a = best 실패·last 성공): −3 dB 9:16 · +0 dB 2:1 · +3 dB 0:3, pooled 11:20 p = 0.15 → 판정하지 못함. F3 가드: V0 만 발동(−3 dB 0.863 … +15 dB 0.239), 나머지 12 arm 발동 없음, genie 해당 없음. GB′ (§5) median 0.5699 (S2 C6 0.283).

**§3 예측 채점**: 0 사전 실현(채점 안 함). 1 판정 1 = (i) ✓, 판정점 −3/0/+3 ✓. 2a R_b\*(−3 dB) 0.60–0.85 ✓ (0.603, 하한 경계값). 2b ΔR CI 가 0 을 걸침 ✗ — CI < 0 (−0.303, −0.110). 3 판정 2 (i) ≥ 10 ✓ (13); 8 개(R0·R1·R3·R4-llr·R4-scvamp·bstar-pilot·ALD·ALDv) 전부 (i) ✓; gmm32·b\*-scalar·R2 중 (i) 아님 ≤ 1 ✓ (0); V1-pilot = (iv)/(iii) ✗ — (i) 2/3. 4 X\* ∈ {ALDv-pilot, V1-pilot} ✓ (V1-pilot); R_X\* 0.3–0.8 ✓ (0.450). 5 genie −3 dB 10–60 ✓ (23). 6 빗나갈 경로 (a)–(d) 없음(ALD 조정 격자 끝 없음, §5).

### 6.2 기록 감사 (Fable 5.1 서브에이전트, 2026-09-28 16:27 CDT = 09-29 06:27 KST; `prereg_audit_2026-09-28/audit_ALD_DOP_ROT_RMX_S2V.md` (`recompute.py` → `recompute.out`); raw npz 에서 독립 재계산 — pair 스크립트 출력 미사용)

정정 없음(수치·라벨·문장·채점 재현). 표현 정정 1 건(본문 반영): ② 대 ① `--ref-arms all` 의 수용 파일 문자열은 `ACCEPT: FAILED` (Stage-C 4 arm 만 다름) — "OK" 는 스크립트 필터 판독.

메모: (1) 2a 는 경계값(0.603 vs 하한 0.60). (2) 판정 2 의 `R0-pilot` 은 @16 판독; @1 판독이면 (i) 3/3 (판정점 +0/+3/+6, 502:0 · 240:2 · 128:1, pooled 870:3), F(−3 dB) 1111, R_X 0.935 [0.921, 0.947] — k = 13·X\* = V1-pilot·문장 조건 불변. (3) 테스트 ALD NMSE(추정 파일 평균, dB, −3..+15): −5.98 −8.73 −11.30 −14.24 −17.14 −20.20 −22.95, 개발(§5) 대비 최대 |차| 0.22 dB; 추정 파일 prov ald.py sha 14121bf8a02d2e01 (조정 때 865261522ca7eade 와 다름 — b233c3a2 의 prov 필드 확장; 알고리즘 상수는 tune json 과 동일).
