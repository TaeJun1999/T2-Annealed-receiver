# NEXT_EXPERIMENTS_FIGHS16e4 — 논문 BLER 곡선의 고SNR 점을 새 시행 n = 20480 으로 (그림 F16 (a)·F17 (a)(b)·F20 (b)·F21·F22·F24 (c)(d)·F31 (b); +6..+15 dB; **보고 전용**, 등록 v2 초안)

- 작성: 2026-10-06 18:23 CDT (= 10-07 08:23 KST) 초안 v1 (Opus 5.5 서브에이전트, 주 세션 지시; 읽기·스모크만, 커밋 없음) → 적대적 검토 1 건 (Fable 5.1 서브에이전트, 2026-10-06 18:50 CDT; MUST 2·SHOULD 6·NIT 12; `prereg_reviews_fighs/review_FIGHS16e4.md`) → **v2** (2026-10-06 19:16 CDT (= 10-07 09:16 KST), Opus 5.5 서브에이전트; 아래 '검토 반영') → **실행 커밋** (§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighs16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 틀: `NEXT_EXPERIMENTS_HISNR16e4.md` v2 (새 시행 10000..30479, n = 20480, chunk 40, `eval_accept --skip0/--points`, 보고 전용, `run_hisnr16e4.sh`) 를 그대로 따르고, 각 arm 의 체크포인트·적합·튜닝·플래그는 그 곡선의 원 raw 를 만든 등록 (`STATIC16e4`/`D3B16e4`/`SVB16e4`/`38901` 의 base 태그, `SPARSE16e4`, `PILOT16e4`, `ROT16e4`, `SUPP16e4`) 의 것을 쓴다. 실행 커밋 = HEAD 조건과 `run|git` 검사 (f) 는 `NEXT_EXPERIMENTS_NSCALE.md` 의 형식.
- **작성 시점 공개**: 사용자 결정 2026-10-06 CDT — 논문 BLER–SNR 그림의 고SNR 구간은 점마다 n = 2560 (실패 몇 개) 이라 SNR 과 함께 튀는 점이 보인다 → 시행을 늘려 다시 그린다; 범위도 사용자가 정했다 (아래). 작성자는 다음을 봤다: (a) 범위 안 그림 스크립트와 그 기록 출력 — 그려지는 모든 곡선의 원 raw (시험 시행 0..2559) 실패 수 (§0.4; 어느 칸이 SNR 과 함께 오르는지 포함); (b) HISNR16e4 §6.1 (D2 C2·C6, V1·b\*·R2·R1·R3·genie, 시행 10000..30479 — 이 등록이 다시 쓰는 시행과 arm); (c) `conference/figures/README.md` 의 Perfect CSI 비단조 재점검 (정적 조건의 오르는 칸 p ≥ 0.27; 도플러는 기준의 성질); (d) runner 로그의 청크 시간 (비용); (e) 이 문서의 스모크 (먼 시행 900000·100000; 명령·구조·시간만, §4). **새로 계산되는 것**: S2c·SV8e·UMi28·MIX3 의 시행 10000..30479 (한 번도 쓰이지 않음, §0.3); D2 C2·C6 의 같은 시행 (HISNR) 에서 아직 없는 arm 6 개 (SBL-loop, SBL-pilot, OMP-pilot, V1-pilot, bstar-pilot, R0-pilot); 회전 15°·30° 채널 (S2 C2 스트림의 같은 시행 번호를 회전시킨 채널) 의 arm 8 개.
- 목적: 범위 안 패널의 +6..+15 dB 점을 SNR 당 새 시행 n = 20480 (원 n 의 8 배; Wilson 폭 ≈ 1/2.8) 으로 그린다. **보고 전용** — 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부" 문장은 원 태그의 것 그대로다.
- 범위 (사용자): `conference/figures/paper_f16.py` (a), `paper_f17.py` (a)(b), `paper_f20.py` (b), `paper_f21.py` (a)–(f), `paper_f22.py` (a)–(f), `paper_f31.py` (b), `paper_f24.py` 의 회전 패널 (c)(d) — 8×4 의 D2 (헤드라인)·D3·SV8e·UMi28·MIX3, D2 회전 15°/30° (정적 학습 prior), D2 16×4 (C6). **범위 밖**: 32×4 (F30 (c)(d)), 파일럿 수 셀 (F19), F24 의 도플러 (a)(b) (고SNR 상승은 기준의 성질: genie 가 H_0 만 안다). 같은 그림 안의 BLER–SNR 곡선이 아닌 패널 — F16 (b) (−3 dB 대 N_train), F17 (c) (−3 dB 회수율), F20 (a)(c) (SNR@0.1·−3 dB 회수율), F31 (a) (판정점 R_X) — 은 바꾸지 않는다.

### v1 → v2 (검토 반영, 항목별; 주 세션 지시 2026-10-06 CDT — MUST·SHOULD 전부, NIT 은 스크립트 값싼 것 4 개 고치고 나머지는 메모)
| 항목 | v2 에서 한 것 | 바뀐 곳 |
|---|---|---|
| MUST-1 집계표의 R0-pilot @1 | §1 보고 행의 "R0-pilot 은 @16 과 @1 둘 다" 를 지웠다 — 집계·그림·예측은 모든 arm @16. 사실 기록: v1 의 집계표에도 `analysis.load_raw` 가 넣는 별칭 줄 `R0-pilot@1` (반복 1 읽기) 이 찍혔다 (스모크 집계표의 arm 이름으로 확인) — 검토의 "스크립트가 내지 않는다" 는 이 별칭을 빠뜨렸다; 약속 문장은 지우고 별칭 줄은 "그림·예측이 쓰지 않는 참고 줄" 로 적는다 | §1 보고 |
| MUST-2 ALD 행 대조가 추정기를 보지 않음 | 검토의 (a) 그대로: phase C 에 **추정기 대조** (`ald_ctl`) — 동결 튜닝 기록·dev·test 파일럿을 `FHCXAROT{a,b}B16e4k` 태그로 복사 (`cp --update=none`), 빈 GPU 1 장에서 `ald.py estimate --set test`, hhat·b·v 를 원 추정 파일과 `np.array_equal` → `results/review_next/FHCXAROT{a,b}B16e4k_aldcontrol.txt` 의 `CONTROL-ALD: OK|FAILED` 와 최대 |차|; phase R 게이트에 건다. GPU 가 Exclusive_Process 라 두 ALD 행의 추정기 대조는 수신기 대조 (병렬) 앞에서 **차례로** 돈다. §1 문장 = "수신기 대조 + 추정기 대조". 동결 전 같은 절차의 확인 (주 세션): 두 원 추정 파일 비트 재현 (§0.5) | §0.5·§1 대조·§1a 18·21·스크립트 `ald_ctl`·phase C·phase R 게이트 |
| S-1 원 ALD 추정·파일럿 sha | 전제에 원 시험 ALD 추정 sha256[:16] (4d053e3e69cea6ce·1ea34f2fb53df32c) 와 dev·test 파일럿 존재; §5 에 파일럿 sha (dev 64939076f196f810·2032a1c8ea447159, test 844d55939b7bb55a·e6c68c6af0f7b72a); §1 의 "ALD 기록 tracked" → "tune 기록 tracked·clean, 추정·파일럿 npz 는 미추적이라 sha 로" | §1 실행·§5·스크립트 전제 |
| S-2 잔존 `_hisnr.npz` | 새 실행: `results/ald/ald_*_hisnr.npz` 가 하나라도 있으면 ABORT (전제); `--resume`: 있는 새 시행 추정 파일은 `prov` (JSON; 키 ald_py_sha·ckpt_sha·device·doppler·git·precision·rotation·train_prior, `git` = `rev-parse --short`) 의 `git` = 실행 HEAD 일 때만 재사용, 아니면 그 행 ABORT | §1 실행·스크립트 전제·`ald_new` |
| S-3 y 축 아래 한계 | 지금 고정: n = 20480 점을 받는 패널 3e-5, F17 은 4e-5 유지 | §1 그림 규칙 |
| S-4 무효·미실행 태그 | 그 곡선은 전 구간 원 raw (n = 2560) 로 두고 밝힌다; 재실행은 사용자 승인 뒤 | §1 그림 규칙 |
| S-5 Fisher 규칙 | 오르는 칸 = BLER 이 바로 아래 SNR 점보다 큰 칸 (같은 n 이면 실패 수; 동률 아님; n 이 다른 +3 → +6 dB 칸도 BLER 로 — 검토의 "실패 수" 정의를 n 이 바뀌는 칸에 맞게 고침), 표·대립가설 (greater) 고정, 그림 기록 텍스트에 반드시, 캡션은 선택 | §1 그림 규칙·§3 예측 2 |
| S-6 스크립트에만 있던 규칙 | REF 미수용 → 종속 행 SKIP, `--resume` 부분집합은 REF 행 포함 → §1 중단·재개; "ALD 2 행은 §4 결정에 따름" → "ALD 2 행 포함" | §1 중단·재개 |
| N-1 | §0.1 첫 행의 arm 열 = 패널별 합집합 명시 | §0.1 |
| N-2 | "(ALD 행이 빠지면 …)" 삭제 (ALD 포함 결정) | §0.1·§3 |
| N-3 | 스모크 잔여물은 주 세션이 삭제; v2 작성 시점에도 없음 | §4 |
| N-4 | 대조 산출물 이름을 §1 실행·§5 에 | §1 실행·§5 |
| N-5 | `run_manifest` 의 rc 를 로그에 (`|| log … rc=$?`) | 스크립트 |
| N-6 | 수신기 대조의 runner 실패를 `$L` 에 | 스크립트 `ctl` |
| N-7 | `cmp_arms` 가 청크 파일 수 = SNR 수 (4) 를 요구 | 스크립트 `cmp_arms`·`ctl` |
| N-8 | ALD 시드가 SNR 인덱스에 매인다는 메모 | §5 |
| N-9 | Wilson z (집계 1.959964, 그림 1.96) 메모 | §1 보고 |
| N-10 | 예측 분모 = 실행·수용된 곡선만; 오르는 칸 정의 | §3 |
| N-11 | runner `_git_head` 워커 캐시 메모 | §0.6 |
| N-12 | `ald.py -h` 가드 삭제 (변경이 실행 커밋에 들어가면 늘 참) | 스크립트 `ald_new` |

## 0. 이미 아는 것 (채점하지 않음)

### 0.1 패널 ↔ 곡선 ↔ raw (그림 이름 → arm 은 `conference/figures/TERMS.md`)
| 데이터셋·조건 (그림 이름) | 패널 | 곡선 = arm | 원 raw (n = 2560, 그림의 −3..+3 dB) | +6..+15 dB 의 n = 20480 출처 |
|---|---|---|---|---|
| Sparse specular 8×4 (D2 C2, 헤드라인 가중치) | F16 (a), F17 (a), F21 (a), F22 (a), F31 (b) | 패널별 합집합: Gaussian prior = R2-ours-G, GMM prior = M-ours-bstar, Proposed = M-ours-dscore-C-V1, Perfect CSI = R5-genie, Turbo LMMSE receiver = R1-turbo, BiG-AMP = R3-bigamp (R1·R3 는 F21 (a) 만, F17 (a) 는 b\*·V1·genie 만) | `raw_B16e4k` | **`raw_HSB16e4k` (HISNR, 있음)** |
| 〃 | F16 (a), F21 (a), F31 (b) | SBL (in loop) = SBL-loop, SBL (pilot-only) = SBL-pilot, OMP (pilot-only) = OMP-pilot | `raw_SPB16e4k` | 새 `FHSPB16e4k` |
| 〃 | F22 (a) | GMM prior, pilot-only = bstar-pilot; Proposed prior, pilot-only = V1-pilot | `raw_PILB16e4k` | 새 `FHPILB16e4k` |
| 〃 | F22 (a) | Pilot-only LMMSE = R0-pilot (그림은 @16) | `raw_B16e4k` | 새 `FHB16e4k` |
| Sparse specular 16×4 (D2 C6) | F17 (b), F21 (b), F22 (b) | V1, b\*, genie, R2, R1, R3 | `raw_NR16B16e4` | **`raw_HSNR16` (HISNR, 있음)** |
| 〃 | F21 (b) / F22 (b) / F22 (b) | 희소 3 / 파일럿 전용 2 / R0-pilot | `raw_SPNR16` / `raw_PILNR16` / `raw_NR16B16e4` | 새 `FHSPNR16` / `FHPILNR16` / `FHNR16B16e4` |
| Sparse specular, CN gains (D3) | F21 (c), F22 (c) | R0-pilot, R1, R2, R3, b\*, V1, genie / 희소 3 / 파일럿 전용 2 | `raw_D3B16e4` / `raw_SPD3` / `raw_PILD3` | 새 `FHD3B16e4` / `FHSPD3` / `FHPILD3` |
| Clustered SV (SV8e) | F21 (d), F22 (d) | 〃 | `raw_SVB16e4` / `raw_SPSV` / `raw_PILSV` | 새 `FHSVB16e4` / `FHSPSV` / `FHPILSV` |
| 3GPP UMi 28 GHz (UMi28) | F20 (b), F21 (e), F22 (e) | 〃 (F20 (b) 는 R2, b\*, V1, genie) | `raw_U28B16e4` / `raw_SPU28` / `raw_PILU28` | 새 `FHU28B16e4` / `FHSPU28` / `FHPILU28` |
| 3GPP mixed (MIX3) | F21 (f), F22 (f) | 〃 | `raw_MXB16e4` / `raw_SPMX` / `raw_PILMX` | 새 `FHMXB16e4` / `FHSPMX` / `FHPILMX` |
| Array rotation 15° (D2 C2, 0° 학습 prior) | F24 (c) | V1, b\*, R2, genie / R1, R3 / V1-pilot / Annealed Langevin (plug-in) = ALD-pilot | `raw_ROTaB16e4k` / `raw_XLROTaB16e4k` / `raw_XPROTaB16e4k` / `raw_XAROTaB16e4k` | 새 `FHROTaB16e4k` (V1 b\* R2 R1 R3 genie) / `FHXPROTaB16e4k` / `FHXAROTaB16e4k` |
| Array rotation 30° | F24 (d) | 〃 | `raw_ROTbB16e4k` / `raw_XLROTbB16e4k` / `raw_XPROTbB16e4k` / `raw_XAROTbB16e4k` | 새 `FHROTbB16e4k` / `FHXPROTbB16e4k` / `FHXAROTbB16e4k` |

F17 (a)(b) 는 HISNR raw 로 이미 다 덮인다 (새 실행 없음). 곡선 76 개를 새로 만든다 (D2 C2·C6 각 6, D3·SV8e·UMi28·MIX3 각 12, 회전 각 8).

### 0.2 다시 쓰는 HISNR raw
`raw_HSB16e4k`·`raw_HSNR16`: 각 npz 2048 (C2 / C6 × +6/+9/+12/+15 dB × 청크 512, skip 10000..30440, n 40), `run|git` 6b1de688, `ACCEPT: OK` (HISNR16e4 §6.1·§6.2 감사 0 오류), arm V1·b\*·R2·R1·R3·genie, 체크포인트·적합 = 원 태그 (`ckpt/d2sx_N160000_a1.pt` 4443921ce8d5c4a1 legacy-last, kron 1024, ll_val −11.459169831224418 / `ckpt/d2sx_NR16_N160000_a1_fb2_best.pt` c050d611b2c714a6 best, kron 4096, 63.1751571838059). 그대로 쓴다; D2 C2·C6 의 새 행은 같은 시행에서 빠진 arm 만 돌리고, 그 genie 를 이 raw 와 비트 대조한다.

### 0.3 시행 10000..30479 의 분리 (작성자 확인 2026-10-06 CDT)
- **raw 청크 이름 전수** (파일은 열지 않고 이름만; `os.listdir`): main `~/t2/conf` + 워크트리 `~/t2_wtB`·`~/t2_wtC`·`~/t2_wtS`·`~/t2_wtSBL`·`~/t2_merge_backup`·`~/t2/.claude/worktrees/{mix3, wf_7003ac6f-b21-1}` 의 `raw*` 406 디렉터리, 청크 164,302 개, 시행 스트림 155 개. [10000, 30480) 와 겹치는 청크는 `raw_HSB16e4k` (S2 Nr8 T16 Tp4, +6/+9/+12/+15) 와 `raw_HSNR16` (S2 Nr16) 의 2048 개씩뿐 (정확히 10000..30479). **30480 이상 청크 0.** 10000 미만의 최대 끝 5760 (`raw_review_next_A1C5_*`).
- **이 등록의 스트림별 기존 사용** (+6..+15 dB, 병합한 구간): S2 Nr8 = 0..3839, 10000..30479 (HISNR); S2 Nr16 = 0..3839, 10000..30479 (HISNR); S2c·SV8e·MIX3 = 0..2559; UMi28 = 0..3839 (2560..3839 = review_next 개발 2560..3199, P3·LO 판정 3200..3839, 규모 확장 1 단계 `raw_S1{D2C2,D2C6,U28C2}` 2560..3839). 스트림 = `common.trial_rng(testbed, prior, Nr, T, Tp, snr)` = `default_rng([20260926, TBID, PID[prior], Nr, T, Tp, snr+100])` (prior·배열·SNR 마다 다른 스트림).
- **로그**: `_skip[1-9][0-9]{4,}_`·`--skip0 ≥ 10000` 을 담은 로그는 main `conf/logs/run_D2_HSB16e4k.log`·`run_D2_HSNR16.log` 뿐, 워크트리 로그 0 (`~/t2_wtS` 의 금지 파일 `*NR32_N160000_a3_fb3*` 은 grep 에서 제외).
- **raw 밖의 사용**: ALD 파일럿·추정 파일 (5 트리, `results/ald/{pilots,ald}_*.npz` 의 `skip`·`n`) = dev 2560..3071, test 0..2559 뿐 (회전 ALD 튜닝 `tune_XAROT{a,b}B16e4k.json` 도 dev_skip 2560, n_dev 512). SPARSE16e4 튜닝 = 전용 스트림 `default_rng([20260930, TBID, PID, Nr, SNR+100])` (`code/sparse_tune.py`; 시드 목록이 달라 어떤 시행과도 무관). PILOT16e4 개발 확인 6400..6439 (raw 삭제, PILOT16e4 머리말), `nuq_coverage_tp.py` 6400..6463, `diag_latent_oracle` 스모크 6400..6401, P3 판정 3200.., A1C5 판정 4480..5759, review_next 개발 2560..; `d2.tests_T2` = `train_rng(which=90)`; σ 격자 `sigma.N_MEAS` 64 (시행 0 부터); `diag_*` 는 시행 0 부터 작은 n.
- **회전**: runner `--rotation` 은 생성기의 AoA 만 돌리고 스트림을 바꾸지 않는다 (같은 난수 → 회전된 H; `ald.py` 주석 "the stream is unchanged"). 회전 행의 시행 번호 10000..30479 는 `raw_HSB16e4k` 와 같은 번호다 — 원 설계와 같은 짝 (ROTa/b 시험 시행 0..2559 = B16e4k 시험 시행 0..2559). 회전 채널에서의 계산은 처음이고, genie 의 H 가 다르므로 HISNR genie 와는 대조하지 않는다 (회전 행끼리 대조).
- 결론: 시행 10000..30479 는 이 등록의 어느 prior·셀·조건에서도 시험·개발·튜닝·판정 집합과 겹치지 않는다. D2 C2·C6 에서는 HISNR (보고 전용 보강) 이 같은 시행을 썼고, 이 등록은 사용자 지시대로 그 시행에 arm 을 더한다.

### 0.4 원 raw 의 고SNR 실패 수 (다시 그리는 곡선; 8 배 = n = 20480 의 기대 실패 수)
| 데이터셋·조건 | 원 raw 실패 수 @16 (n = 2560), +6/+9/+12/+15 dB — 그 arm 의 곡선이 다시 그려진다; ↑ = 그 구간에 오르는 칸 있음 |
|---|---|
| D2 C2 (새 arm 만) | R0-pilot 63/35/28/14; SBL-loop 48/25/27/10 ↑; SBL-pilot 51/27/28/10 ↑; OMP-pilot 77/62/60/34; V1-pilot 17/6/6/3; bstar-pilot 33/15/16/10 ↑ |
| D2 C6 (새 arm 만) | R0-pilot 41/22/12/8; SBL-loop 27/8/10/7 ↑; SBL-pilot 33/15/15/7; OMP-pilot 39/22/14/13; V1-pilot 9/2/1/2 ↑; bstar-pilot 24/16/10/5 |
| D3 | R0-pilot 218/97/60/30; R1 298/136/84/40; R2 199/75/57/22; R3 403/294/348/356 ↑; b\* 111/53/36/12; V1 64/27/22/5; genie 35/10/14/3 ↑; SBL-loop 143/62/53/16; SBL-pilot 154/67/47/16; OMP-pilot 221/116/71/49; V1-pilot 80/31/25/7; bstar-pilot 132/62/39/12 |
| SV8e | R0-pilot 6/1/0/0; R1 5/2/0/1 ↑; R2 2/0/0/0; R3 25/17/14/26 ↑; b\* 0/0/0/0; V1 0/0/0/0; genie 1/0/0/0; SBL-loop 2/0/0/0; SBL-pilot 3/0/0/0; OMP-pilot 12/1/0/0; V1-pilot 0/0/0/0; bstar-pilot 0/0/0/0 |
| UMi28 | R0-pilot 371/190/92/51; R1 440/228/107/57; R2 334/172/80/48; R3 745/715/777/766 ↑; b\* 243/126/69/27; V1 215/104/44/24; genie 58/26/8/3; SBL-loop 291/150/66/42; SBL-pilot 307/166/77/44; OMP-pilot 492/278/152/80; V1-pilot 229/106/53/26; bstar-pilot 264/132/76/31 |
| MIX3 | R0-pilot 408/236/113/58; R1 540/303/140/79; R2 378/214/103/49; R3 758/753/793/785 ↑; b\* 243/135/58/16; V1 193/104/41/17; genie 68/35/13/2; SBL-loop 317/183/84/31; SBL-pilot 351/193/94/40; OMP-pilot 601/358/207/93; V1-pilot 217/106/45/20; bstar-pilot 266/144/71/19 |
| 회전 15° | R2 76/34/19/15; b\* 43/17/11/8; V1 20/10/6/3; genie 9/4/3/4 ↑; R1 121/67/31/22; R3 141/132/142/145 ↑; V1-pilot 23/10/6/3; ALD-pilot 41/20/7/4 |
| 회전 30° | R2 78/35/27/22; b\* 51/29/19/12; V1 29/11/7/6; genie 13/5/2/3 ↑; R1 128/72/45/31; R3 173/164/172/171 ↑; V1-pilot 31/12/6/6; ALD-pilot 58/19/13/11 |

오르는 칸이 있는 곡선 15/76 (그중 R3-bigamp 6 개 — 약 5 % 바닥의 평평한 곡선; R3 를 빼면 9/70). SV8e 는 +9..+15 dB 에서 대부분의 arm 이 0/2560 이라 n = 20480 에서도 실패가 몇 개 (기대 ≤ 8) 에 그친다.

### 0.5 코드·자원
- 수신기 경로 코드 마지막 변경: `arms.py` 2381af57 (09-30 KST, SPARSE), `d2.py` 2640bb87·`sv.py` 093ffa4e (09-28), `score.py` d9085247 (09-23), `bigamp.py`·`scvamp.py` (09-20), Demo (09-18); `mix3.py` 의 그 뒤 변경은 UMi28 Nr 16/32 상수 추가뿐 (Nr 8 불변); `runner.py`·`common.py` 의 그 뒤 변경은 C9 셀·Nr 가드·`--worker-gb` (Nr 8/16 경로 불변). 원 raw 중 가장 늦은 SP raw (02dafa1c) 이후 수신기 코드 변경 없음. 그 이전 raw 의 기본 14 arm 은 ROT0 대조 (6 데이터셋, a4cbd184)·NSCALE bridge (`BRB32e4`·`BRNR16B16e4`, 68d4d353, `--ref-arms all`) 가 비트 재현을 보였다. 파일럿 전용·희소·ALD arm 과 회전 경로를 현재 코드로 다시 돌린 대조는 없다 → §1 대조.
- v1 작성 때 `code/ald.py regen` 은 시행 집합으로 dev (2560..) 와 test (0..2559) 만 만들었다 → 주 세션이 `--set hisnr` (skip `C.HISNR_SKIP0`, n 20480, SNR 6/9/12/15) 를 넣었다 (§4; 실행 커밋 전에 커밋). ALD 추정은 GPU (ALD16e4 의 예외: 사전 계산만 GPU, 수신기는 CPU). **추정기 재현 — 동결 전 확인 (주 세션, 시험 집합 0..2559 만)**: 동결 튜닝 기록과 dev·test 파일럿의 스크래치 사본으로 `ald.py estimate --set test` 를 GPU 0 에서 다시 돌리면 원 `ald_XAROTaB16e4k.npz`·`ald_XAROTbB16e4k.npz` 의 hhat (7, 2560, 32)·b·v 가 비트 동일 (`np.array_equal` True, 최대 |차| 0); 스크래치 파일 삭제 — §1 추정기 대조의 근거.
- 시행 재생성 비용 (작성자 측정, 단일 프로세스·유휴, `run_task` 의 skip 루프와 같은 생성·송신; 시행 스트림이 아닌 난수로): S2 C2 0.121, S2 C6 0.130, S2c 0.125, SV8e 0.162, **UMi28 10.3, MIX3 9.3 ms/시행** (스모크: skip 100000 의 38.901 청크 전체가 953–1150 s → 실제 스트림 ≤ 9.5 ms/시행). runner 는 청크마다 skip 앞의 시행을 다시 만든다 → 새 실행의 평균 skip 20220 (원 raw 1260) 이라 38.901 청크마다 ≈ +195 s (UMi28)·+176 s (MIX3), S2 계열 ≈ +2–3 s (전부 부하에서는 더 길 수 있다).

### 0.6 그 밖
- HISNR 의 그림 F32 (원 시행과 새 시행을 나란히) 는 이 등록의 범위 밖이며 그대로다.
- runner `_git_head()` 는 워커마다 한 번 계산해 캐시한다 — 긴 행 중간에 conf/code 가 더러워져도 그 워커의 뒤 청크 `run|git` 에 `+dirty` 가 붙지 않을 수 있다; HEAD 이동은 행마다의 HEAD 검사와 (f) 가 잡는다 (검토 N-11, 메모만).
- `run_manifest.py` 는 skip ≥ 10000 raw 의 분할을 "HISNR16e4 high-SNR supplement set (trials >= 10000)" 으로 적는다 — 같은 시행 집합이라 사실과 맞다 (코드 변경 없음).

## 1. 고정되는 것
| 항목 | 값 |
|---|---|
| 태그·arm·플래그 | §1a 의 24 행 (표 순서 = 실행 순서). runner 공통: `--testbed D2 --prior <P> --cell <C> --chunk 40 --ntrain 160000 --snr 6 9 12 15 --n 20480 --skip0 10000 --arm <arms> --tag <TAG>`. 체크포인트 (`--stagec-ckpt`), GMM 적합 (링크 `results/gmm_fits_D2_<TAG> → gmm_fits_D2_<원 적합>`), 희소 pick (`--sparse-file`, SPARSE16e4 의 pick, sha 고정), ALD 튜닝 기록 (`results/ald/tune_XAROT{a,b}B16e4k.json`, 고정), 그 밖 플래그 (`--pilot-arms`, `--rotation`, `--ald-file`) 는 그 arm 의 원 raw 와 같다; SP 행은 원 SP raw 처럼 `--stagec-ckpt` 없이. arm 은 그림이 그리는 것만 (+ genie). 파일럿 전용 arm 의 구성 (`--pilot-arms`: 채널 사후를 파일럿에서 한 번 만들고 고정, 검출·복호만 16 반복) 과 그림의 읽기 (F22 의 R0-pilot @16) 는 원 raw 와 같다. CPU complex128, 16 반복 |
| SNR · 시행 | +6, +9, +12, +15 dB; 시행 10000..30479 (`common.HISNR_SKIP0`; SNR 당 n = 20480, 청크 40 × 512). D2 C2·C6 는 `raw_HSB16e4k`·`raw_HSNR16` 과 같은 시행 (짝). 그림의 −3/0/+3 dB 점은 원 raw (시행 0..2559) 그대로 |
| 대조 (**HISNR 에 없던 추가**; 수신기 대조 + 추정기 대조) | 실행 맨 앞 (phase C). **(1) 추정기 대조 (ALD 2 행, 차례로)**: 동결 튜닝 기록 `tune_XAROT{a,b}B16e4k.json` 과 dev·test 파일럿 `pilots_XAROT{a,b}B16e4k_{dev,test}.npz` 를 `FHCXAROT{a,b}B16e4k` 태그로 복사 (`cp --update=none`; 덮어쓰지 않음) 하고 빈 GPU 1 장에서 `ald.py estimate --tag FHC… --ckpt ckpt/d2sx_N160000_a1.pt --set test` → `results/ald/ald_FHCXAROT{a,b}B16e4k.npz` 의 hhat·b·v 가 원 `ald_XAROT{a,b}B16e4k.npz` (4d053e3e69cea6ce·1ea34f2fb53df32c) 와 **비트 동일** (`np.array_equal`) 해야 한다 → `results/review_next/FHCXAROT{a,b}B16e4k_aldcontrol.txt` 의 `CONTROL-ALD: OK|FAILED` (+ 최대 |차|). 같은 절차의 동결 전 확인은 §0.5 (두 파일 비트 재현). **(2) 수신기 대조 (24 행, 병렬)**: 각 행의 **같은 runner 명령**을 이미 관측된 시험 청크 0 (시행 0..39) 의 +6/+9/+12/+15 dB 에 돌린다 (태그 `FHC…`, 행마다 4 청크) — 모든 arm × `common.KEYS_RAW` (blk_err, ber, nmse, tauL_gmean, alphaD, tauL_clip_frac, alphaD_clip; 16 반복) 이 원 raw (§1a ORIG; 회전 루프 행은 ROT·XL 두 raw) 의 같은 이름 청크와 **비트 동일** (NaN = NaN), 청크 파일 수 = SNR 수 (4) → `results/review_next/FHC…_control.txt` 의 `CONTROL: OK|FAILED`. ALD 행의 수신기 대조는 원 시험 ALD 추정 파일을 입력으로 쓴다. 두 대조 중 하나라도 OK 가 아니면 그 행은 돌리지 않고 원인 기록 (§6), 재실행은 사용자 승인. 목적: 그림이 한 곡선으로 잇는 두 시행 집합의 점이 같은 수신기·같은 추정기 (현재 코드·같은 플래그·같은 arm 부분집합·동결 튜닝) 에서 나온다는 것. 새 정보 없음 (이미 관측된 시행) |
| 수용 (태그마다) | (a) `eval_accept.py --prior <P> --ntrain 160000 --bstar <b*> [--kron-K K] --ll-val <ll> --n 20480 --skip0 10000 --points <C>:6,9,12,15 --tag <TAG>:<role>:<sha>:<C> [--ref-raw raw_<REF>]` → 점 집합·청크 계획 {(10000 + 40k, 40)} × 4 점, meta ntrain·bstar·kron_K·ll_val, ckpt sha·role (SP 행은 `-:-` = Stage C id 없음), iters 16; **genie 재현**: D2 C2 행 = `raw_HSB16e4k`, D2 C6 행 = `raw_HSNR16`, 새 데이터셋·회전의 SP/PIL/XP/XA 행 = 같은 데이터셋·조건의 첫 행 (base / 루프) — 모든 시행·반복 비트 동일 (blk_err, ber, tauL_gmean, alphaD). (f) 모든 청크의 `run|git` = 실행 커밋 (+dirty 없음); SP 행 `meta|sparse` = pick 의 그 SNR 값; 회전 행 `meta|rotation` = `deg=<V>`; ALD 행 `meta|ald_file` = 새 추정 파일 경로 + sha256[:16]. (g) `run_manifest.py --tag <TAG>`. 수용 실패 → 그 태그 무효·집계표 없음·원인 §6, 재실행은 사용자 승인. raised 시행은 실패로 남는다 (01_RULES §4; 개수 보고) |
| 보고 (전부 보고 전용) | 태그마다 `results/review_next/fighs_<TAG>.txt`: SNR × arm 의 실패 / n, BLER, 95% Wilson (`hisnr_report.wilson`, z = 1.959964; raised 블록 = 실패). 모든 arm 은 @16 (그림의 읽기; `analysis.load_raw` 가 넣는 별칭 줄 `R0-pilot@1` 도 찍히지만 그림·예측은 쓰지 않는다). **검정·라벨 없음.** 그림은 아래 규칙으로 다시 그리고, 그림 스크립트는 새 raw 의 실패 수를 이 집계표와 assert 한다 (그림 쪽 Wilson 은 각 스크립트의 z = 1.96 — 구간의 넷째 자리가 다를 수 있다; assert 는 실패 수만) |
| 그림 규칙 (지금 고정) | 범위 안 패널의 모든 곡선: −3/0/+3 dB = 원 raw (n = 2560), +6/+9/+12/+15 dB = n = 20480 raw (§0.1 의 출처). 한 점은 한 raw (두 n 을 합치지 않는다). 오차 막대는 지금 막대를 그리는 곡선 (F16 (a) 의 네 arm, F17 (a)(b), F20 (b)) 에만, 점마다 **그 점의 n** 으로 95% Wilson; 막대가 없는 패널 (F21, F22, F24 (c)(d), F31 (b), F16 (a) 의 희소 3 곡선) 은 그대로 없다. 실패 0 점은 그 패널의 기존 표기 (F17·F21·F22 의 화살표는 그 점 n 의 95% Wilson 상한 z²/(n + z²) — n = 2560 1.5e-3, n = 20480 1.9e-4 — 에서 아래로; 곡선은 거기서 끊김). 캡션에 두 시행 집합 (시험 시행 0..2559 의 n = 2560 at −3..+3 dB; 새 시행 10000..30479 의 n = 20480 at +6..+15 dB) 을 밝힌다. y 축 아래 한계: n = 20480 점을 받는 패널 (F16 (a), F20 (b), F21, F22, F24 (c)(d), F31 (b)) 은 **3e-5** (0 이 아닌 최소 BLER 1/20480 = 4.9e-5 와 0 점 화살표 상한 1.9e-4 가 모두 보이는 가장 가까운 3·1 격자값; 지금은 2e-4·1.5e-4·5e-4); F17 은 4e-5 유지. 무효 (수용 실패)·미실행 (대조 실패·REF 미수용·실행 실패) 태그의 곡선은 원 raw (n = 2560) 점을 전 구간 그대로 두고 캡션·그림 기록 텍스트에 '이 곡선은 전 구간 n = 2560' 을 밝힌다 — 재실행은 사용자 승인 뒤이며, 그때까지 곡선을 반쯤 바꾸지 않는다. 실행 뒤에도 오르는 칸 — BLER (실패 / n) 이 바로 아래 SNR 점보다 **큰** 칸 (같은 n 이면 실패 수가 큰 칸; 동률은 오름 아님; n 이 다른 +3 → +6 dB 칸도 BLER 로 비교) — 이 있으면 칸마다 그림 기록 텍스트에 **반드시** 단측 Fisher p 를 적는다: 표 [[f_hi, n_hi − f_hi], [f_lo, n_lo − f_lo]] (hi = 높은 SNR), 대립가설 = 높은 SNR 의 BLER 이 더 크다 (`scipy.stats.fisher_exact(table, alternative='greater')`), SNR 점마다 독립 시행; 캡션에는 선택. 평활·재실행·점 빼기 없음 |
| 다중성 | 라벨·검정 없음 → 해당 없음. Fisher p 는 서술용 |
| 비용 | §1b — CPU 192 워커 전부, 합계 ≈ 19 h (§1b; 범위 ≈ 18–22 h — base·R0 행은 상한, 38.901 재생성 몫은 유휴 측정 기준이고 전부 부하에서 1.5–2 배면 +1.6–3.3 h). ALD 추정만 GPU 1 장 × 수 분 |
| 실행 | `bash code/run_fighs16e4.sh` (tmux, main `~/t2/conf`). 전제: conf/code·Demo 청결, 이 문서·DECISIONS tracked·clean, **HEAD = 실행 커밋** (`git log -1 -- <이 문서>` = HEAD; 실행 중 HEAD 가 움직이면 ABORT), `raw_FH*` 없음, `results/ald/ald_*_hisnr.npz` 없음 (`--resume` 이면 그 파일의 `prov` git = HEAD 일 때만 재사용), `raw_HSB16e4k`·`raw_HSNR16` 완전 (2048), ckpt·pick sha = §1a, 원 시험 ALD 추정 sha256[:16] = 4d053e3e69cea6ce·1ea34f2fb53df32c, ALD 튜닝 기록 `tune_XAROT{a,b}B16e4k.json` tracked·clean (추정·파일럿 npz 는 미추적이라 sha 로 — 추정은 전제, dev·test 파일럿은 §5). CPU 전용 (`CUDA_VISIBLE_DEVICES=`); GPU 는 ALD 추정기 대조 (phase C, 차례로) 와 새 시행 ALD 추정 (phase R) 에서만 빈 GPU 1 장 (`nvidia-smi` memory.used < 100 MiB 확인, 자동 재시도 없음). 산출물: 행마다 `raw_<TAG>`·`logs/run_D2_<TAG>.log` (덧붙임, 머리 줄)·`results/review_next/{<TAG>_accept.txt, fighs_<TAG>.txt, run_manifest_<TAG>.json}`; 대조 `raw_FHC…` 24 (4 청크씩, 시행 0..39)·`results/review_next/FHC…_control.txt` 24·`results/review_next/FHCXAROT{a,b}B16e4k_aldcontrol.txt` 2·`logs/run_D2_FHC….log` 24·`results/ald/{tune_*.json, pilots_*_dev.npz, pilots_*_test.npz, ald_*.npz}` 의 `FHCXAROT{a,b}B16e4k` 판 8; 새 시행 ALD `results/ald/{pilots,ald}_XAROT{a,b}B16e4k_hisnr.npz` 4; 적합 링크 `results/gmm_fits_D2_FH…`·`FHC…` 48. 로그 `logs/run_fighs16e4.log` (CDT), 끝 `FIGHS_DONE ok=<n> fail=<n>` (종료 코드 = fail). 실행 중 다른 CPU 작업 없음, main 커밋 없음. 장시간 → 사용자 승인 뒤 |
| 중단·재개 | `bash code/run_fighs16e4.sh --resume [TAG …]`: 같은 커밋의 `start (git …)` 로그 줄이 있을 때만. 읽을 수 없는 청크 파일은 `raw_<TAG>.truncated/` 로 옮기고 (지우지 않음) runner 가 끝난 청크를 건너뛴다; 대조·수용·집계는 다시 실행. REF 행 (genie 재현 기준) 이 수용되지 않으면 종속 행 (같은 데이터셋·조건의 SP/PIL/XP/XA) 은 돌리지 않고 SKIP (fail 로 셈); `--resume` 의 TAG 부분집합은 각 행의 REF 행을 포함해야 한다 (REF 행은 다시 수용되고 끝난 청크는 건너뜀). 끝난 태그의 재실행은 사용자 승인. 결과를 본 뒤 행을 빼거나 n·SNR 을 바꾸지 않는다 — 24 행 전부 실행·보고 (ALD 2 행 포함; §4 결정 2026-10-06 18:33 CDT) |
| 순서 | D2 C2 (SP → PIL → R0) → D3 → SV8e → UMi28 → MIX3 (각 base → SP → PIL) → 회전 15° (루프 → XP → XA) → 회전 30° → D2 C6 (PIL → R0 → SP). 싼 것·본문 그림 (F16 (a), F31 (b)) 먼저; 대조 (phase C) 는 맨 앞에 병렬 |

### 1a. 태그 (24 행; `code/run_fighs16e4.sh` 의 ROWS 와 같다)
| # | TAG | 데이터셋·조건 | arm | 추가 플래그 | ckpt (sha256[:16] · role) | b\* · ll_val | genie 재현 (REF) | 대조 기준 (ORIG) |
|---|---|---|---|---|---|---|---|---|
| 1 | FHSPB16e4k | D2 C2 | SBL-loop SBL-pilot OMP-pilot R5-genie | `--sparse-file results/sparse/pick_S2_C2.json` (2a6d79a23b6b6501) | — (없음) | kron 1024 · −11.459169831224418 | raw_HSB16e4k | raw_SPB16e4k |
| 2 | FHPILB16e4k | D2 C2 | V1-pilot bstar-pilot R5-genie | `--pilot-arms` | d2sx_N160000_a1.pt (4443921ce8d5c4a1 · legacy-last) | 〃 | raw_HSB16e4k | raw_PILB16e4k |
| 3 | FHB16e4k | D2 C2 | R0-pilot R5-genie | — | 〃 | 〃 | raw_HSB16e4k | raw_B16e4k |
| 4 | FHD3B16e4 | D3 (S2c) C2 | R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie | — | d2sx_S2c_N160000_a1_best.pt (7ebf4e6647d4413f · best) | kron 4096 · 0.08879931165293979 | — | raw_D3B16e4 |
| 5 | FHSPD3 | 〃 | 희소 3 + genie | `--sparse-file …pick_S2c_C2.json` (afdb48498c76b88c) | — | 〃 | FHD3B16e4 | raw_SPD3 |
| 6 | FHPILD3 | 〃 | V1-pilot bstar-pilot R5-genie | `--pilot-arms` | 〃 (7ebf…) | 〃 | FHD3B16e4 | raw_PILD3 |
| 7 | FHSVB16e4 | SV8e C2 | base 7 (4 행과 같음) | — | d2sx_SV8e_N160000_a1_best.pt (d2d78962c2846364 · best) | gmm256 · −47.80545576704972 | — | raw_SVB16e4 |
| 8 | FHSPSV | 〃 | 희소 3 + genie | `--sparse-file …pick_SV8e_C2.json` (72a6500e72950141) | — | 〃 | FHSVB16e4 | raw_SPSV |
| 9 | FHPILSV | 〃 | 파일럿 전용 2 + genie | `--pilot-arms` | 〃 (d2d7…) | 〃 | FHSVB16e4 | raw_PILSV |
| 10 | FHU28B16e4 | UMi28 C2 | base 7 | — | d2sx_UMi28_N160000_a1_best.pt (6f3a1b9490864af1 · best) | kron 4096 · 5.797910431000217 | — | raw_U28B16e4 |
| 11 | FHSPU28 | 〃 | 희소 3 + genie | `--sparse-file …pick_UMi28_C2.json` (3d27f1bb72865fa5) | — | 〃 | FHU28B16e4 | raw_SPU28 |
| 12 | FHPILU28 | 〃 | 파일럿 전용 2 + genie | `--pilot-arms` | 〃 (6f3a…) | 〃 | FHU28B16e4 | raw_PILU28 |
| 13 | FHMXB16e4 | MIX3 C2 | base 7 | — | d2sx_MIX3_N160000_a1_best.pt (b591ae24ae3c5f31 · best) | kron 4096 · 33.7604873920761 | — | raw_MXB16e4 |
| 14 | FHSPMX | 〃 | 희소 3 + genie | `--sparse-file …pick_MIX3_C2.json` (baffec3e463ad6b3) | — | 〃 | FHMXB16e4 | raw_SPMX |
| 15 | FHPILMX | 〃 | 파일럿 전용 2 + genie | `--pilot-arms` | 〃 (b591…) | 〃 | FHMXB16e4 | raw_PILMX |
| 16 | FHROTaB16e4k | D2 C2 회전 15° | M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R1-turbo R3-bigamp R5-genie | `--rotation 15` | d2sx_N160000_a1.pt (4443… · legacy-last) | kron 1024 · −11.459169831224418 | — | raw_ROTaB16e4k + raw_XLROTaB16e4k |
| 17 | FHXPROTaB16e4k | 〃 | V1-pilot R5-genie | `--rotation 15 --pilot-arms` | 〃 | 〃 | FHROTaB16e4k | raw_XPROTaB16e4k |
| 18 | FHXAROTaB16e4k | 〃 | ALD-pilot R5-genie | `--rotation 15 --ald-file …/results/ald/ald_XAROTaB16e4k_hisnr.npz` (§4; 수신기 대조 입력·추정기 대조 기준 = `ald_XAROTaB16e4k.npz` 4d053e3e69cea6ce, 전제에서 sha 검사) | 〃 | 〃 | FHROTaB16e4k | raw_XAROTaB16e4k |
| 19 | FHROTbB16e4k | D2 C2 회전 30° | 16 행과 같음 | `--rotation 30` | 〃 | 〃 | — | raw_ROTbB16e4k + raw_XLROTbB16e4k |
| 20 | FHXPROTbB16e4k | 〃 | V1-pilot R5-genie | `--rotation 30 --pilot-arms` | 〃 | 〃 | FHROTbB16e4k | raw_XPROTbB16e4k |
| 21 | FHXAROTbB16e4k | 〃 | ALD-pilot R5-genie | `--rotation 30 --ald-file …/ald_XAROTbB16e4k_hisnr.npz` (수신기 대조 입력·추정기 대조 기준 = `ald_XAROTbB16e4k.npz` 1ea34f2fb53df32c, 전제에서 sha 검사) | 〃 | 〃 | FHROTbB16e4k | raw_XAROTbB16e4k |
| 22 | FHPILNR16 | D2 C6 | V1-pilot bstar-pilot R5-genie | `--pilot-arms` | d2sx_NR16_N160000_a1_fb2_best.pt (c050d611b2c714a6 · best) | kron 4096 · 63.1751571838059 | raw_HSNR16 | raw_PILNR16 |
| 23 | FHNR16B16e4 | D2 C6 | R0-pilot R5-genie | — | 〃 | 〃 | raw_HSNR16 | raw_NR16B16e4 |
| 24 | FHSPNR16 | D2 C6 | 희소 3 + genie | `--sparse-file …pick_S2_C6.json` (3958df589e385522) | — | 〃 | raw_HSNR16 | raw_SPNR16 |

희소 3 = SBL-loop SBL-pilot OMP-pilot; 파일럿 전용 2 = V1-pilot bstar-pilot; base 7 = R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie. 희소 pick 의 +6..+15 dB 값 (ρ_SBL, ρ_OMP; n_em/L): S2 C2 16, 16; 10/6, 10/8, 10/12, 10/32 · S2c 16, 16; 10/6, 10/8, 10/8, 10/12 · SV8e 16, 16; 3/32, 5/32, 5/32, 5/32 · UMi28 8, 16; 3/32, 5/32, 5/32, 5/32 · MIX3 16, 16; 5/32, 5/32, 5/32, 5/32 · S2 C6 16, 16; 5/8, 5/8, 10/8, 10/12. ALD 튜닝 (c = 0.01, β = 0.005; 멈춤 스텝 +6/+9/+12/+15): 15° 434/536/600/600, 30° 428/535/600/600.

### 1b. 비용 (CPU 192 워커; 시간 = 2048 태스크 × 청크당 시간 / 192)
청크당 시간 = 같은 arm 집합의 원 raw 로그의 +6..+15 dB 평균 (전부 부하) + 재생성 차이 (§0.5). base 행 (4·7·10·13) 은 ROT\<suf\> (V1·b\*·R2·genie) + XLROT\<suf\> (R0·R1·R3 + 그 밖 4 arm) 의 합이라 **상한**; R0 행 (3·23) 은 XL 로그 (8 arm) 라 상한. 검산: HISNR C2 (6 arm) 로그 평균 243 s → 2048 × 243 / 192 = 43 min, 실측 44.4 min; C6 2745 s → 488 min, 실측 500.3 min. 스모크 열 = §4 의 청크 1 개 시간 (단일 워커·8 프로세스 동시). 대부분이 먼 skip 의 재생성 (S2 계열 skip 900000 ≈ 110–146 s, 38.901 skip 100000 ≈ 950 s) 이고, 나머지 수신 몫은 전부 부하 로그의 약 1/2–1/5 (예: SP C2 ≈ 62 s 대 253 s, D3 base ≈ 190 s 대 ≤ 474 s; ROT0B16e4k 14 arm 청크 단일 워커 198 s 대 전부 부하 B16e4k 660 s) 라 비용은 로그 열로 잡는다.

| # | TAG | arm | 원 raw 로그의 청크당 s (+6..+15 평균, 전부 부하) | + 재생성 차이 s | 청크당 s | 시간 (min) | 스모크 청크 1 개 s (skip) |
|---|---|---|---|---|---|---|---|
| 1 | FHSPB16e4k | 희소 3 + genie | SPB16e4k 253 | 2 | 255 | 45 | 171 (900000) |
| 2 | FHPILB16e4k | 파일럿 전용 2 + genie | PILB16e4k 32 | 2 | 34 | 6 | 119 (900000) |
| 3 | FHB16e4k | R0-pilot + genie | XLROTaB16e4k 32 (8 arm; 상한) | 2 | ≤ 34 | ≤ 6 | 116 (900000) |
| 4 | FHD3B16e4 | base 7 | ROTaD3 387 + XLROTaD3 87 | 2 | ≤ 476 | ≤ 85 | 302 (900000) |
| 5 | FHSPD3 | 희소 3 + genie | SPD3 249 | 2 | 251 | 45 | 174 (900000) |
| 6 | FHPILD3 | 파일럿 전용 2 + genie | PILD3 87 | 2 | 89 | 16 | 129 (900000) |
| 7 | FHSVB16e4 | base 7 | ROTaSV 181 + XLROTaSV 24 | 3 | ≤ 208 | ≤ 37 | 202 (900000) |
| 8 | FHSPSV | 희소 3 + genie | SPSV 155 | 3 | 158 | 28 | 192 (900000) |
| 9 | FHPILSV | 파일럿 전용 2 + genie | PILSV 70 | 3 | 73 | 13 | 152 (900000) |
| 10 | FHU28B16e4 | base 7 | ROTaU28 407 + XLROTaU28 122 | 196 | ≤ 725 | ≤ 129 | 1115 (100000) |
| 11 | FHSPU28 | 희소 3 + genie | SPU28 106 | 196 | 302 | 54 | 1003 (100000) |
| 12 | FHPILU28 | 파일럿 전용 2 + genie | PILU28 170 | 196 | 366 | 65 | 957 (100000) |
| 13 | FHMXB16e4 | base 7 | ROTaMX 407 + XLROTaMX 125 | 176 | ≤ 708 | ≤ 126 | 1150 (100000) |
| 14 | FHSPMX | 희소 3 + genie | SPMX 179 | 176 | 355 | 63 | 991 (100000) |
| 15 | FHPILMX | 파일럿 전용 2 + genie | PILMX 167 | 176 | 343 | 61 | 953 (100000) |
| 16 | FHROTaB16e4k | V1 b* R2 R1 R3 genie | ROTaB16e4k 209 + XLROTaB16e4k 32 (HSB16e4k 같은 6 arm 243) | 2 | 243 | 43 | 186 (900000) |
| 17 | FHXPROTaB16e4k | V1-pilot + genie | XPROTaB16e4k 30 | 2 | 32 | 6 | 116 (900000) |
| 18 | FHXAROTaB16e4k | ALD-pilot + genie | XAROTaB16e4k 8 (+ ALD regen·GPU 추정 수 분) | 2 | 10 | 2 | — (ALD: §4) |
| 19 | FHROTbB16e4k | V1 b* R2 R1 R3 genie | ROTbB16e4k 209 + XLROTbB16e4k 32 | 2 | 243 | 43 | 192 (900000) |
| 20 | FHXPROTbB16e4k | V1-pilot + genie | XPROTbB16e4k 33 | 2 | 35 | 6 | 118 (900000) |
| 21 | FHXAROTbB16e4k | ALD-pilot + genie | XAROTbB16e4k 7 (+ ALD 수 분) | 2 | 9 | 2 | — (ALD: §4) |
| 22 | FHPILNR16 | 파일럿 전용 2 + genie | PILNR16 174 | 2 | 176 | 31 | 198 (900000) |
| 23 | FHNR16B16e4 | R0-pilot + genie | XLROTaNR16 314 (8 arm; 느슨한 상한 — 스모크 수신 몫 ≈ 6 s) | 2 | ≤ 316 | ≤ 56 | 123 (900000) |
| 24 | FHSPNR16 | 희소 3 + genie | SPNR16 943 | 2 | 945 | 168 | 495 (900000) |

| 묶음 | D2 C2 | D3 | SV8e | UMi28 | MIX3 | 회전 15° | 회전 30° | D2 C6 | 대조 (phase C) | 합계 |
|---|---|---|---|---|---|---|---|---|---|---|
| 시간 (min) | 58 | 145 | 78 | 247 | 250 | 51 | 51 | 256 | ≈ 15 | ≈ 1151 (≈ 19.2 h) |

## 2. 원고 문장 범위
"+6 dB 이상 점은 SNR 당 새 시행 n = 20480 (시행 10000..30479), −3..+3 dB 점은 시험 시행 n = 2560" 처럼 그림 캡션·본문에서 **두 시행 집합을 밝힌 보고 전용 보강**으로만 쓴다. 등록된 판정점·라벨·"전부" 문장·회수율·SNR@0.1 은 원 태그의 것이다. 새 raw 의 수로 새 비교 주장을 만들지 않는다.

## 3. 미리 적는 예측 (보고 전용; 적중/빗나감만 기록)
채점의 분모는 실행·수용된 곡선만이다 (행이 빠지면 아래의 304·70·24 가 그만큼 줄어든다).
1. 다시 그리는 곡선 76 개 × 4 SNR = 304 칸 중 **≥ 90 %** 에서 새 점추정 (n = 20480) 이 원 raw (n = 2560) 의 95% Wilson 구간 안에 든다 (HISNR 예측 3 의 몬테카를로: 칸당 ≈ 0.94).
2. R3-bigamp 를 뺀 다시 그리는 곡선 70 개 중 +6 → +9 → +12 → +15 dB 에서 오르는 칸 (§1 그림 규칙의 정의: BLER 이 바로 아래 SNR 점보다 큰 칸, 동률 아님) 이 하나라도 있는 곡선이 **원 raw 의 9 개보다 적다** (§0.4).
3. D3·SV8e·UMi28·MIX3·회전 15°·30° 의 4 SNR (24 칸) 에서 V1 실패 ≤ b\* 실패 (같은 시행, 동률 포함) 가 **≥ 22/24** 칸 (원 raw: MIX3 +15 dB 만 V1 17 > b\* 16, SV8e +6..+15 는 0 = 0).

## 4. 선행 작업
| 항목 | 상태 |
|---|---|
| `code/ald.py` 의 새 시행 집합 — `--set hisnr` (regen: skip `C.HISNR_SKIP0`, n 20480, SNR 6/9/12/15; 나머지는 기존 경로: estimate 는 이미 `ald_<TAG>_<set>.npz` 를 쓰고 `tune_<TAG>.json`·dev 파일럿 대조를 그대로 한다; runner `_ald_table`·`ALDSitePrior` 는 파일의 `skip` 으로 시행을 찾는다). XA 2 행 (18·21) 의 전제 | **작성 (2026-10-06 18:33 CDT, 주 세션; 결정: 넣는다 → XA 2 행 실행)** — `code/ald.py` 3 줄 (`snrs` = 6/9/12/15 for hisnr, `skip, n` 표에 `"hisnr": (C.HISNR_SKIP0, 20480)`, `--set` choices 에 hisnr) + docstring 1 줄; 기존 dev·test 경로 불변. 스모크 (사본: HISNR_SKIP0 → 900000, n 40; 스모크 태그 `fhsmkald` 에 tune·dev 파일럿 사본): regen (CPU, 4 SNR × 40, 112 s) → estimate (GPU 0) → runner `--rotation 15 --ald-file … --arm ALD-pilot R5-genie --skip0 900000 --n 40 --snr 15` 1 청크 rc 0 (1.9 min); 스모크 파일은 모두 삭제. 등록 시행 10000..30479 는 쓰지 않았다 |
| 스크립트 `code/run_fighs16e4.sh` | 작성 (`bash -n` 통과). 스모크: **스모크 완료** (2026-10-06 17:47:59–18:14:42 CDT 본 스모크, 18:15–18:22 CDT 재개 시험; 시각은 `logs`·`launch.log` 의 `date` 출력; HEAD a83849d4, conf/code·Demo 청결 → `run|git` 깨끗). 배포본에서 sed 로 만든 사본 (바꾼 것만: `SK/N/SNRS` → 먼 시행·n 40·+15 dB, 출력 경로 → 스크래치, 태그 접두 FH → fhsmk, HISNR 기준 → 같은 셀의 첫 스모크 행, `# PRE` 전제 줄·`# CTL` 대조 줄 삭제; 38.901 의 SP·PIL 4 행은 병렬이라 REF `-`) 으로 ALD 2 행을 뺀 **22 행**을 행마다 청크 1 개 (+15 dB) 로 실행 — S2·S2c·SV8e 스트림 skip 900000, UMi28·MIX3 스트림 skip 100000 (38.901 생성기 ≈ 10 ms/시행이라 900000 이면 청크당 ≈ 2.5 h), 8 프로세스 × 1 워커. 결과: runner rc 0 22/22; `eval_accept` **ACCEPT: OK 22/22** (점·청크 계획·meta·ckpt id; genie 재현은 같은 셀 첫 행 대비); (f) **OK 22/22** (`run|git` a83849d4, `meta|sparse` 6 행, `meta|rotation` 4 행); raised 시행 0; `run_manifest` 22; 집계표 22 (구조만 확인 — 스모크 시행의 BLER 은 보지 않았다; runner 의 done 줄이 R2·R3·genie 의 반올림 BLER 을, 집계표 머리 한 줄이 OMP-pilot 0/40 을 보여 준 것은 공개; 시행 900000·100000 은 어떤 등록에도 쓰이지 않는다). 38.901 4 행의 genie 재현은 따로 `eval_accept --ref-raw raw_fhsmk{U28,MX}B16e4` 로 OK 4/4, 다른 스트림 대비 음성 대조는 FAILED (기대대로). 청크 시간 = §1b 마지막 열. **대조 (phase C)** 는 시행 0..39 를 쓰므로 스모크하지 않았다 — 24 개 명령을 dry-run 으로 출력해 확인 (ALD 행은 시험 추정 파일로 바뀜), 비교 함수 `cmp_arms` 는 스모크 raw 로 5 경우 (일치 2, 회전 대 정적 genie 불일치, 참조에 없는 arm, 두 참조 중 첫 보유 raw) 가 기대대로. 전제 검사 4 경우 (미추적 등록 → ABORT; HEAD ≠ 실행 커밋 → ABORT; raw 있음 → ABORT; `--resume` 인데 그 커밋의 start 줄 없음 → ABORT), ALD 행은 `ald.py` 변경 없이 runner 를 부르지 않고 ABORT. `--resume`: 잘린 청크를 `raw_<TAG>.truncated/` 로 옮기고 다시 계산 → 수용 OK, 다시 계산한 청크 = 원래 청크 (21 비교, 0 차이; 재현성). 최종 스크립트는 스모크한 텍스트와 주석 1 줄, 쓰지 않는 import, runner 로그 덧붙이기 (머리 줄 포함), 대조 본문의 함수 `ctl` 화, 잘린 청크 검사의 `.truncated` 제외만 다르며, 최종 텍스트로 재개 시험 2 회와 phase C dry-run 을 다시 했다. 잔여물 (`raw_fhsmk*` 24 디렉터리 = 22 + `raw_fhsmkPILB16e4k.truncated{,.truncated}`, `results/gmm_fits_D2_fhsmk*` 링크 22, `results/review_next/run_manifest_fhsmk*.json` 22) 은 주 세션이 삭제 (아래 결정 행); v2 작성 시점 확인: 없음 |
| 주 세션 결정 (2026-10-06 18:33 CDT) | 대조 phase (C) 유지 (두 시행 집합을 한 곡선으로 잇는 근거); 오차 막대는 기존 패널 관례 (점마다 자기 n, 막대 없는 패널은 그대로); F32 는 범위 밖; 비용 절감안 (38.901 행 합치기·chunk 변경·SV8e 제외) 은 쓰지 않는다; 스모크 잔여물 (raw 24·링크 22·manifest 22) 삭제 |
| v2 스크립트 재검사 (2026-10-06 19:16 CDT (= 10-07 09:16 KST)) | `bash -n` 통과. **phase C dry-run** (명령만 출력; 24 행 전부의 정적 전제 — 새 ALD sha 검사 포함 — 통과): ALD 추정기 대조 2 개 (복사 3 + `ald.py estimate --tag FHCXAROT{a,b}B16e4k --ckpt ckpt/d2sx_N160000_a1.pt --set test` + 비교) 가 차례로, 수신기 대조 24 개 (청크 수 4 요구) 가 병렬로 나오고, conf 에 만들어진 링크·ALD 파일 0. **ALD 추정기 대조 실제 1 회** (19:06 CDT; XAROTa, 스모크 태그 `fhsmkCXAROTaB16e4k`, 시험 집합 0..2559, GPU 0, ≈ 35 s): `CONTROL-ALD: OK`, hhat (7, 2560, 32)·b·v 최대 |차| 0; phase R 게이트의 grep 통과. **SP 1 행 스모크** (19:07–19:10 CDT; skip 900000, +15 dB, 1 워커, 청크 173 s): `eval_accept` OK, 그러나 (f) 가 `run|git a83849d4+dirty` 를 **기대대로 거부** (conf/code 에 주 세션의 미커밋 `ald.py` 변경과 이 스크립트가 있다 — 실제 실행에서는 전제 검사가 먼저 막는다). **재개 시험** (19:11–19:14 CDT; 잘린 청크 → `raw_<TAG>.truncated/` 로 이동 → 재계산 173 s; runner 로그는 머리 줄과 함께 덧붙여져 두 실행의 청크 줄이 모두 남는다; 스모크 사본에서만 (f) 가 `+dirty` 를 받게 한 줄 바꿈): 수용 OK·집계표 작성, 재계산 청크 = 원 청크 (28 비교, 0 차이). 곁가지로 확인: 사본의 H 를 바꾼 첫 시도에서 행마다의 HEAD 검사가 ABORT, 청크 0 개일 때 `cmp_arms` 가 "expected 1" 로 FAILED. **전제 단위 시험**: 새 실행 + `ald_*_hisnr.npz` 있음 → ABORT, 없음 → 통과, `--resume` → 통과; `ald_new` 재사용 규칙 = prov git 이 HEAD 이면 재사용 (rc 0), 아니면 ABORT (rc 1); 원 ALD 추정 sha 가 등록값과 다르면 ABORT, 같으면 통과. 이번 시험 잔여물 (주 세션 삭제): `raw_fhsmkSPB16e4k`·`raw_fhsmkSPB16e4k.truncated`, 링크 `results/gmm_fits_D2_fhsmkSPB16e4k`, `results/review_next/run_manifest_fhsmkSPB16e4k.json`, `results/ald/{tune_fhsmkCXAROTaB16e4k.json, pilots_fhsmkCXAROTaB16e4k_dev.npz, pilots_fhsmkCXAROTaB16e4k_test.npz, ald_fhsmkCXAROTaB16e4k.npz}` |
| 2 라운드 검토 (Fable, 검토 파일 '## Round 2') | **MUST 0**. 반영 (주 세션): S2-1 — `ctl`·`ald_ctl` 이 시작할 때 판정 파일을 비우고 (조기 반환이 묵은 OK 를 남기지 않게), 새 실행 전제에 FHC 대조 산출물 없음 추가; N2-2 — 추정기 대조 입력 `pilots_XAROT{a,b}B16e4k_test.npz` sha256[:16] (844d55939b7bb55a · e6c68c6af0f7b72a) 를 전제에서 검사; N2-3 — n = 20480 ALD 추정은 스모크하지 않았다 (스모크 n 40; `ald_run` 은 남길 스텝만 저장해 메모리는 배치 8 배 수준; 실패하면 18·21 행만 SKIP); N2-5 — §3 오르는 칸: +3→+6 dB 칸은 기록만, 예측 2 의 분자에 넣지 않는다 (§0.4 기준이 +6..+15). N2-1·N2-4 는 그대로 (종속 행 SKIP 으로 안전; `cp --update=none` 은 새 전제로 무해) |
| 적대적 검토 (Fable 서브에이전트) → v2 | 끝남 (1 라운드 → v2, 2 라운드 MUST 0) |
| 실행 커밋 (§5 채움 + 스크립트 + DECISIONS 동결 줄) · 사용자 승인 (≈ 19 h, 범위 18–22 h, CPU 전부) | 끝남 — §5 를 채운 이 커밋 |

## 5. 평가 전 고정 기록 (실행 커밋에서 채운다)
| 항목 | 값 |
|---|---|
| 실행 커밋 | (이 표를 채운 커밋 — 자기 해시는 커밋 안에 쓸 수 없으므로 `logs/run_fighs16e4.log` 의 `start (git …)` 줄과 raw `run|git` 으로 §6 에 적는다) |
| ALD 결정 (§4) · `ald.py` 선행 코드 커밋 || 넣는다 (XA 2 행 실행). `code/ald.py` 변경 (3 줄 + docstring) 은 별도 선행 커밋 없이 **이 실행 커밋에 함께** 들어간다; 스모크·추정기 재현 증거는 §0.5·§4 |
| 실행 커밋의 conf/code·Demo 가 선행 코드 커밋과 같음 (`git diff --stat`) || 해당 없음 (선행 코드 커밋 = 이 커밋). 이 커밋의 conf/code 변경은 `code/ald.py` (M) 와 `code/run_fighs16e4.sh` (A) 뿐, Demo 변경 없음 |
| 체크포인트 sha256[:16] 6 개 (재확인; §1a 와 같아야) || 전부 일치 (주 세션 재계산): d2sx_N160000_a1.pt 4443921ce8d5c4a1 · d2sx_S2c_N160000_a1_best.pt 7ebf4e6647d4413f · d2sx_SV8e_N160000_a1_best.pt d2d78962c2846364 · d2sx_UMi28_N160000_a1_best.pt 6f3a1b9490864af1 · d2sx_MIX3_N160000_a1_best.pt b591ae24ae3c5f31 · d2sx_NR16_N160000_a1_fb2_best.pt c050d611b2c714a6 |
| 희소 pick sha256[:16] 6 개 (재확인; tracked·clean) || 전부 일치·tracked·clean: pick_S2_C2 2a6d79a23b6b6501 · pick_S2c_C2 afdb48498c76b88c · pick_SV8e_C2 72a6500e72950141 · pick_UMi28_C2 3d27f1bb72865fa5 · pick_MIX3_C2 baffec3e463ad6b3 · pick_S2_C6 3958df589e385522 |
| ALD 기록 sha256[:16] (v2 작성 시점 값 — 실행 커밋에서 재확인) | 원 시험 추정 `ald_XAROTaB16e4k.npz` 4d053e3e69cea6ce · `ald_XAROTbB16e4k.npz` 1ea34f2fb53df32c (전제 검사); dev 파일럿 `pilots_XAROTaB16e4k_dev.npz` 64939076f196f810 · `pilots_XAROTbB16e4k_dev.npz` 2032a1c8ea447159; test 파일럿 (추정기 대조 입력) `pilots_XAROTaB16e4k_test.npz` 844d55939b7bb55a · `pilots_XAROTbB16e4k_test.npz` e6c68c6af0f7b72a; 튜닝 기록 (tracked) `tune_XAROTaB16e4k.json` 6dd071bcd697d5d2 · `tune_XAROTbB16e4k.json` 46da6a9477252a72; 재확인 값: |
| 대조 산출물 (§1 실행) | 수신기 대조 `raw_FHC…` 24·`FHC…_control.txt` 24; 추정기 대조 `FHCXAROT{a,b}B16e4k_aldcontrol.txt` 2·`results/ald/*FHCXAROT{a,b}B16e4k*` 8 |
| ALD 시드 메모 (검토 N-8) | `ald.py estimate` 의 Langevin 시드는 SNR 인덱스 k 에 매인다 (`SEED + 1000 + 17 k`): hisnr 파일 (SNR 6/9/12/15) 의 k = 0..3 은 시험 파일 (7 SNR) 의 −3/0/+3/+6 dB 추정과 같은 시드를 쓴다 — 시행이 달라 통계적 결과는 없다 |
| `raw_HSB16e4k`·`raw_HSNR16` (청크 수, `run|git`, 수용 파일) || 각 2048 청크; run|git 6b1de688 (HISNR 실행, `logs/run_hisnr16e4.log` 의 start 줄); 수용 `HSB16e4k_accept.txt`·`HSNR16_accept.txt` = `ACCEPT: OK` |
| 스모크 (§4) 의 최종 판 (커밋될 스크립트와 같은 텍스트에서 만든 사본) || v1 스모크 22 행 + v2 재시험 (SP 1 행·재개·ALD 추정기 대조 1 회, 모두 먼 시행) — 배포본 sed 사본. 2 라운드 반영 (판정 파일 비우기 2 줄·전제 2 줄) 뒤에는 `bash -n` 만 (동작 경로 불변) |
| 적대적 검토 원문 경로 · 반영 요약 || `results/review_next/prereg_reviews_fighs/review_FIGHS16e4.md` — 1 라운드 MUST 2·SHOULD 6·NIT 12 → v2 반영 (표: 문서 머리); 2 라운드 **MUST 0**, SHOULD 1·NIT 5 → S2-1·N2-2 스크립트, N2-3·N2-5 문서 (§4 의 2 라운드 행) |
| 사용자 승인 (장시간 CPU, 시각은 `date` 로) || 사용자 선택 (이 문서 작성 줄 18:23 CDT 이전): 범위 '본문+정적 그림 (권장)' — 그 선택지 설명 '등록·검토 약 3 h + CPU 약 15–20 h → 10-08 CDT 무렵 그림 완성'; 이어서 사용자 '화이팅해서 끝까지 서둘러 진행하자'. §1b 추정 19.2 h 는 승인 범위 안 |
| DECISIONS 동결 줄 || `[2026-10-07 09:29 KST] FIGHS16e4 동결 = 실행 커밋` (conf/DECISIONS.md 끝) |

## 6. 결과 (이 절은 추가만 한다)
