# 적대적 검토 — NEXT_EXPERIMENTS_HISNR16e4.md v1 (고SNR 보강, D2 C2·C6 +6..+15 dB, 새 시행 10000..30479, 보고 전용) + 선행 코드 9356aca5 (2026-09-29 22:59 CDT = 09-30 12:59 KST; Fable 5.1 서브에이전트; main HEAD 207cca1d, 초안 untracked)

읽기 전용 조사. `run_hisnr16e4.sh`·runner·eval_accept·hisnr_report 는 **실행하지 않았고** GPU 도 쓰지 않았다. 본 것: 초안 전문; `git show 9356aca5` (5 파일 diff); `common.py` (SKIP0 상수, `trial_rng`), `runner.py` (`chunk_plan`, `run_task` 재생성 루프 :526–535, `cmd_run`, 인자 검증 :1173–1300), `analysis.py:118–187` (`load_raw`), `eval_accept.py` 전문, `run_manifest.py` 전문, `hisnr_report.py`, `genie_floor.py`, `pair_tags.py:1–60,119–127`, `ald.py:92,288`, `Demo/exp_0921_analysis.py:44–51` (`sign_p`·`paired`), `Demo/t2_route_a.py:287–293` (`transmit`), `run_supp16e4.sh` DS 표, `WORK_QUEUE.md` 3b, `genie_floor/genie_floor_raw_B16e4k.txt`, `logs/run_D2_{B16e4k,NR16B16e4,DOPaB16e4k,DOPaNR16,XLDOPaB16e4k,XLDOPaNR16,PILNR16}.log` 의 청크 시간. 작은 CPU 검사 (OMP 2): 218 `raw_*` + `raw/` 의 청크 **이름** 전수 (skip 최대·첫 청크 분포·`load_raw` 오프셋 규칙 구/신 비교), `raw_B16e4k`·`raw_NR16B16e4` 의 +15 dB 청크 0 meta 키와 +6..+15 dB 실패 수 (6 arm), `raw_PILB16e4k`·`raw_XLDOPaB16e4k` 의 `meta|stagec_ckpt_id`, 두 ckpt 의 오늘 sha256[:16], 시행 재생성 비용 (3000 시행), 예측 3 의 몬테카를로 (R = 20000).

**검증되어 문제 없는 것은 C 절.** 요지: 시행 독립성·오프셋 규칙·sha/role/ll_val·러너 재개·통계 함수는 맞다. 그러나 스크립트는 **수용 검사가 반드시 실패**하도록 돼 있고 (7 점 요구), C6 비용은 **≈ 8 배 과소**, 예측 1 의 도구 (`genie_floor.py`) 는 시행 0 부터 재생성해 새 raw 에 **정렬되지 않으며**, 예측 3 은 **방향이 거꾸로**라 거의 확실히 빗나간다.

---

## A. 반드시 (동결 전 고침)

1. **`eval_accept` 는 셀 격자 7 점 (−3..15) 을 요구하므로 4 점짜리 raw_HS\* 는 항상 `ACCEPT: FAILED` → 스크립트가 두 태그를 모두 INVALID 로 찍고 보고를 내지 않는다.** 위치: `eval_accept.py:75` `want = {(c, s) for c in cells for s in points.get(c, C.CELLS[c]["snrs"])}` → `set(pts) != want` → `"points [...] missing/extra"`; `run_hisnr16e4.sh:22–23` 은 `--points` 를 주지 않는다. 초안 §1 수용 행의 "청크 {(10000 + 40k, 40)} × 4 점" 은 코드와 다르다. 고정안 (1 토큰): 스크립트의 eval_accept 호출에 `--points $CELL:6,9,12,15` (선례 `run_dop16e4.sh:36`, `run_pareto_eval.sh:49`); §1 수용 행에 `--points <CELL>:6,9,12,15` 를 명기. 청크 계획 검사는 `plan = [(10000 + 40k, 40)]` 512 개로 이미 맞다 (C.4).

2. **비용 행이 C6 에서 ≈ 8 배 과소다 — "C6 ≈ 1 h" 가 아니라 ≈ 7.5 h.** 근거 (같은 arm 집합의 실측): `raw_DOPaNR16` (V1·b\*·R2·genie, C6) 청크 40 시행 = **2420–2452 s** (−3 과 +15 dB 같음; 448 태스크 192 워커 3 라운드 = 112 min ✓); `raw_XLDOPaNR16` (8 baseline, R1·R3 포함) 335 s → R1+R3 ≤ 100 s. 이 실행: 4 점 × 512 = **2048 태스크 / 192 워커 = 11 라운드 × ≈ 2500 s ≈ 7.6 h**. C2: `raw_DOPaB16e4k` 161–171 s + R1/R3 (`XLDOPaB16e4k` 8 arm 33 s) ≈ 175 s → 11 × 175 s ≈ **32 min** (초안 0.3–0.5 h 는 대체로 맞음). 합계 ≈ **8.2 h, 192 코어 전부** (SBL #4 등 다른 CPU 작업이 그동안 막힘). 재생성 오버헤드는 아니다 (C.5: 0.17 ms/시행, 태스크당 ≤ 5 s). 고정안: §1 비용 행을 "C2 ≈ 0.5 h, C6 ≈ 7.5 h (DOPa 실측 청크 시간 × 11 라운드)" 로; WORK_QUEUE 3b 의 "CPU 수 시간" 도 같이. 장시간 실행이므로 사용자 승인을 **동결 전에** 받고, 대안이 있으면 지금 정한다 (예: C6 만 n = 10240 → ≈ 3.8 h; 또는 그대로) — 결과를 본 뒤 n 을 줄이는 것은 불가.

3. **예측 1 의 도구 `genie_floor.py` 는 스트림의 시행 0 부터 재생성한다 — skip 10000 인 raw 에 그대로 쓰면 채널과 실패가 1 만 시행 어긋나고, 초안은 이를 "가능하면" 으로 선택 사항으로 둔다.** 위치: `genie_floor.py:33–37` `rng = C.trial_rng(...)` 뒤 `for tr in range(len(fails))` — raw 의 청크 이름 (`skip10000`) 을 읽지 않는다; 초안 §1 보고 행 "genie 실패의 L 분포 (…가능하면)"; `run_hisnr16e4.sh` 는 genie_floor 를 호출하지 않는다 → 결과를 본 뒤 손으로 돌리거나 건너뛸 수 있는 자리. 고정안 (코드 ≈ 4 줄): `genie_floor.py` 에 `--skip0` (기본 0) 을 두고 루프 전에 `for _ in range(skip0)` 로 시행당 같은 4 회 소비 (`gen.sample`, `integers(K)`, `permutation(Ns)`, `standard_normal((Nr,T))` × 2 — `run_task` :528–532·`transmit` :292 와 동일, C.1) 를 하거나 raw 의 최소 skip 을 읽어 자동으로 맞춘다; `hisnr_report` 뒤에 스크립트가 두 태그 모두 `genie_floor.py --raw raw_$TAG --prior S2 --cell $CELL --snrs 6 9 12 15 --skip0 10000 > results/review_next/genie_floor/genie_floor_raw_$TAG.txt` 를 **무조건** 실행; §1 의 "가능하면" 삭제. 정렬 확인 한 줄 (출력의 실패 수 = hisnr_report 의 genie 실패 수) 을 §5 에 적는다.

4. **예측 3 은 방향이 거꾸로라 설계상 거의 확실히 빗나간다.** 원문: "원 태그 (n = 2560) 의 점추정이 **이 실행의** 95% Wilson 구간 안에 … ≥ 14/16". n = 20480 의 구간은 n = 2560 추정치의 표준편차보다 좁다 (√8 배). 몬테카를로 (원 실패 수를 참값으로, 16 칸, R = 20000): 쓰인 대로 칸당 포함 확률 **0.45–0.49** → P(≥ 14/16) ≈ **0.001**; 거꾸로 ("이 실행의 점추정이 **원 태그의** 95% Wilson 안에") 0.93–0.94 → P(≥ 14/16) ≈ **0.93**. 고정안: 예측 3 을 "이 실행의 V1·b\* 점추정이 원 태그 (n = 2560) 의 95% Wilson 구간 안에 든다 — 16 칸 중 ≥ 14" 로 바꾼다 (또는 두 비율 검정 p ≥ 0.05 가 ≥ 14/16).

5. **`run_manifest.py` 가 이 raw 의 분할을 "A1C5 judging set (trials >= 4480)" 로 적는다 — 거짓 기록.** 위치: `run_manifest.py` `trial_stream.split` — `min(skips) >= C.A1C5_SKIP0` 가 첫 분기라 10000 도 거기 걸린다 (`HISNR_SKIP0` 분기 없음). 9356aca5 는 manifest 를 건드리지 않았다. 고정안 (1 줄): `"HISNR16e4 report-only supplement (trials >= %d)" % C.HISNR_SKIP0 if min(skips) >= C.HISNR_SKIP0 else ...` 를 맨 앞에. (`sample_counts.test_trials_per_point` 가 20480 으로 찍히는 것도 이름이 어긋나지만 값은 맞다 — 그대로 두되 §5 에 한 줄.)

6. **"점당 실패 ~100 건 목표" 는 관심 arm (V1) 에서 설계상 달성되지 않는다 — 수를 적어 두라.** 원 실패 수 × 8 = 기대값: **V1** C2 128 / 56 / 40 / 24, C6 48 / 16 / 16 / 16 (+6/+9/+12/+15); **b\*** C2 224 / 136 / 128 / 64, C6 176 / 112 / 80 / 40; **genie** C2 72 / 16 / 16 / 16, C6 48 / 8 / 16 / 0. V1 +9..+15 dB 는 두 셀 모두 16–56 건이고 ~100 건이 되려면 n ≈ 8.5e4 (C2) / 1.3e5 (C6) 가 필요하다. 고정안: 목적 문장을 "점당 b\* ≥ 40, V1 ≥ 16 정도의 실패 (기대값 표) 로 Wilson 구간 폭을 원 태그의 ≈ 1/√8 로" 처럼 기대값으로 바꾸거나, n 을 늘리려면 지금 (반드시 2 의 비용과 함께) 정한다.

## B. 권고

7. **재개 규칙이 없다.** `run_hisnr16e4.sh:11` 은 `raw_HS*` 가 있으면 ABORT — ≈ 8 h 실행이 중단되면 (SUPP 처럼 서버 재시작) 손으로 스크립트를 고치거나 raw 를 지워야 한다. 고정안: `resume` 인자 — `raw_$TAG` 가 있고 `results/review_next/${TAG}_accept.txt` 가 없으며 HEAD = 로그 `start (git …)` 의 커밋일 때만 통과; 모든 청크를 `np.load` 로 열어 잘린 npz 를 지운 뒤 (SUPP 재개 때 "잘린 npz 0" 검사) runner 가 완료 청크를 건너뛰게 한다 (`run_task` :481). §1 에 "재개 = 같은 커밋·청크 삭제 없음·로그에 표기; 그 밖의 재실행 = 사용자 승인".

8. **`hisnr_report` 가 조용히 넘어가는 것 두 가지 + 스크립트의 rc 처리.** (a) `arms = [x for x in (...) if x in d[keys[0]]]` — arm 이 빠지면 말없이 빼고, V1/b\* 가 빠지면 `paired` 가 KeyError; (b) `load_raw` 경고는 개수만 찍는다 (NaN 으로 채워진 키가 실패로 세어질 수 있음 — 러너가 요청 arm 누락에 예외를 내므로 실제로는 생기기 어렵지만 검사는 공짜). 고정안 (≈ 3 줄): 6 arm 모두 있고 경고 0 이 아니면 `sys.exit(1)`; 스크립트 :27 은 `rc=$?` 를 보지 않고 `OK` 를 올린다 → rc ≠ 0 이면 FAIL. 출력 파일 첫 줄에 `# run_hisnr16e4 git <HEAD> <date>` (accept/report 둘 다), 끝에 `exit $FAIL`, `log` 를 `logs/queue.log` 에도 (SUPP 와 같이).

9. **수용 실패 뒤의 규칙을 §1 에 적어라.** 스크립트는 INVALID 로 찍고 보고를 내지 않지만 문서에는 없다: "수용 실패 → 보고 없음, raw 보존, 원인 §6 기록, 재실행은 사용자 승인" (SUPP §1 선례). `hisnr_report.py` 는 무효 raw 에도 손으로 돌릴 수 있으니 이 문장이 결과 뒤 선택을 막는 유일한 장치다.

10. **그림 규칙을 지금 정하라.** 초안은 표에서 "나란히 적되 합치지 않는다" 만 말한다. 원고 곡선 (F-그림) 이 고SNR 점을 이 raw 로 **바꾸거나** 두 n 을 합치는 것을 §2 에서 금지하고, 허용 형태를 하나로: "등록 곡선은 raw_B16e4k / raw_NR16B16e4 그대로; 보강은 별도 표시 (예: 속 빈 마커 + 'n = 20480 supplement') 의 덧그림 또는 별도 표".

11. **예측을 더 날카롭게 (선택).** 예측 2 (V1 ≤ b\* 점추정 4 × 2) 는 기대값 (반드시 6) 으로 보아 거의 확실하다. 추가 후보: "C6 +9..+15 dB genie 실패 ≤ 0.1 % 이고 있으면 전부 L = 3" (원 3/7680); "V1 실패 / b\* 실패 ≤ 0.6 이 8 점 모두"; "b\*-only : V1-only 부호검정 p < 1e-3 이 +6 dB 두 셀에서". 그리고 SUPP 형식의 "0. 이미 관측된 것 (채점 안 함)" 에 원 실패 수 표 (반드시 6 의 값 ÷ 8) 를 둔다.

12. **작성 시점 공개를 구체화.** "두 raw 의 고SNR 실패 수와 genie 바닥" 외에 같은 SNR 의 공개 기록 (SUPP/DOP/ROT/PIL/ALD 24 조건의 +6..+15 dB, `tables_D2_*.txt` TABLE A) 도 봤음을 적고, **왜 C2·C6 만인지** (헤드라인 + 공차원 셀; D3·SV·U28·MX 는 안 함) 한 줄 — 없으면 사후 선택으로 읽힌다.

13. **기록 잔손질.** `load_raw` 의 주석 (:130–132) 과 `runner.py --skip0` 도움말, `eval_accept.py` 모듈 docstring 이 HISNR 을 언급하지 않는다; `meta|em_sec_note` 는 링크 이름 (`gmm_fits_D2_HSB16e4k`) 을 적을 것이다 — 원 태그와 같은 디렉터리라는 것을 §5 에 (`readlink`). `hisnr_report` 의 SNR 별 n 은 `arms[0]` 의 길이 하나만 본다 — 6 arm 길이 동일 검사를 8 에 포함.

14. **동시 실행 조건.** C6 가 192 코어를 7.5 h 잡는다. 큐에서 SEEDS3 BLER 뒤로 두는 것은 맞지만, 그동안 CPU 가 필요한 것 (SBL 튜닝 #4, 감사 스크립트) 이 있으면 순서를 사용자가 정하도록 §1 비용 행에 "192 코어 전부, 동시 CPU 작업 불가" 를 적는다.

## C. 확인 (문제 없음; 근거)

1. **시행 10000..30479 는 어디서도 쓰이지 않았다.** 218 `raw_*` + `raw/` 의 청크 이름 전수: skip 최대 **5720** (`raw_review_next_A1C5_*`, 4480 + 32 × 40 = 5760 끝), 그 다음 4470 (K2, n 10), 4460 (K1·LO); 태그 없는 `raw/` 최대 2520 (+40 = 2560); `~/t2` 전체에 `_skip1xxxx_`·`_skip[1-9]xxxx_` 파일 0. 코드 쪽: `ald.py:92` dev = 2560..2560 + n_dev (기본 512), test = 0..2559; `diag_latent_oracle` 스모크 6400..6401 (raw 삭제됨); `diag_p1_cavity` = dev 청크. 스트림은 `trial_rng(testbed, prior, Nr, T, Tp, snr)` = `default_rng([SEED, TBID, PID, Nr, T, Tp, snr+100])` — C2 (Nr 8) 와 C6 (Nr 16) 은 다른 스트림, +6..+15 dB 는 원 태그가 0..2559 를 쓴 **같은** 스트림의 더 먼 구간이라 "새 시행" 이면서 같은 분포다. 재생성은 `run_task` :526–535 (sample → integers(K) → permutation(Ns) → `transmit` 의 `standard_normal((Nr,T))` × 2; `tr < skip` 이면 버림) 이라 chunk 가 어디서 시작하든 시행 k 는 같다 (test C4 의 성질) ✓.

2. **`load_raw` 오프셋 규칙: 기존 raw 전부 동작 불변.** 219 디렉터리 1373 점의 청크 이름으로 `max(s for s in tuple if s <= first)` + 연속 검사를 구 튜플 `(0, 2560, 3200, 4480)` 과 신 튜플로 계산: 시작점·ok 가 **0 점에서 다름, 경고 0**; 첫 청크 분포 {0: 1323, 2560: 20, 3200: 12, 4480: 18} — (4480, 10000) 구간이나 ≥ 10000 에서 시작하는 raw 는 없다. 새 raw 에서 첫 청크 10000 이 빠지면 10040 ≠ 10000 → 경고 ✓; 꼬리 청크 누락은 `load_raw` 가 못 보지만 `eval_accept` 청크 계획 검사가 잡는다 ✓.

3. **다른 코드의 가정.** `pair_tags.py:119–127` 은 DEV_SKIP0 하나로 test/dev 를 가르므로 raw_HS\* 를 "dev" 로 보고 §0 수용 (`DEV_CHUNKS` 16 × 40) 에서 **거부**한다 — 안전 (쓰이지도 않음). `p3_rules.load(skip0=…)`·`a1c5_report`·`k1_report`·`diag_*` 는 자기 상수를 쓴다. 영향받는 것은 `run_manifest` 의 분할 라벨뿐 (반드시 5).

4. **`eval_accept --skip0` 와 값들.** `plan = [(10000 + 40k, 40) for k in range(512)]` = `runner.chunk_plan(10000, 20480, 40)` (:118) ✓; meta 검사는 첫 (10000)·끝 (30440) 청크 ✓; `--n 20480 --chunk 40` 은 나누어떨어짐 ✓. 스크립트 표의 sha·role·b\*·K·ll_val = SUPP DS 표 1·6 행 = 원 raw meta (`raw_B16e4k` +15 dB 청크 0: `meta|bstar kron`, `kron_K 1024`, `ll_val|kron −11.459169831224418`; `raw_NR16B16e4`: `kron 4096`, `63.1751571838059`, `meta|stagec_ckpt_id … c050d611b2c714a6 … role=best`) = 오늘 파일 sha256[:16] (`ckpt/d2sx_N160000_a1.pt` **4443921ce8d5c4a1**, `ckpt/d2sx_NR16_N160000_a1_fb2_best.pt` **c050d611b2c714a6**) ✓. `raw_B16e4k` 자체에는 `meta|stagec_ckpt_id` 가 없지만 (P0-1 이전) 새 raw 는 러너가 쓴다: 같은 ckpt 로 돈 `raw_PILB16e4k`·`raw_XLDOPaB16e4k` 의 값 `sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 | BEST_WEIGHTS_UNAVAILABLE …` → `role=legacy-last` 검사 통과 (SUPP 24/24 와 같은 경로) ✓.

5. **러너 호출.** `--skip0 10000`·`--arm`·`--stagec-ckpt`·`--ntrain 160000` 모두 `changed` 에 들어가 `--tag` 필수 → 주어짐 ✓; `--snr 6 9 12 15` → 4 점 × 512 = 2048 태스크, skip 오름차순 정렬 ✓; 완료 청크는 `exists` 로 건너뜀 ✓ (재개는 권고 7). 재생성 비용 실측 **0.173 ms/시행 (C2), 0.176 (C6)** → 마지막 태스크 5 s, 평균 3–4 s = C2 청크의 ≈ 2 %, C6 의 < 0.2 % ✓. 적합 링크 `results/gmm_fits_D2_HS<TAG> → gmm_fits_D2_{B16e4k,NR16B16e4}` 는 DOP/ROT/PIL/XL 24 개와 같은 형태이고 대상은 실제 디렉터리 (9/22, 9/25) ✓ → b\* 선택 (검증 ll) 이 같은 파일에서 같은 값 ✓. σ 격자는 ckpt 의 `sigma_tag` 로 (`score.py:1392–1399`; NR16 → `results/sigma_grid_D2_NR16.npz` 존재) — 원 실행과 동일 ✓. CUDA: `export CUDA_VISIBLE_DEVICES=` + `run` 은 `--device cpu` 외 거부 (:1237) + `run_manifest` 가 스스로 숨김 ✓. 전제 검사 (`conf/code`·`Demo` 청결은 `-C` 로 저장소 상대경로, 문서·DECISIONS 는 cwd conf 상대경로 — 둘 다 옳음), 러너에 `< /dev/null` ✓.

6. **보고 스크립트.** `wilson` 은 표준식, k = 0 → 하한 0 ✓; `paired(d, "M-ours-bstar", "M-ours-dscore-C-V1")` → (b\*만 실패, V1만 실패) 이므로 출력 라벨 "b\* only : V1 only" 순서 ✓; `sign_p` = `2·Σ_{i≤min} C(n,i)/2^n` 정수 정확 계산 (`exp_0921_analysis.py:44–46`), n_d 는 수백 (b\*-only 기대 최대 ≈ 200) → ms ✓; raised 블록은 `load_raw` 가 1.0 으로, 스크립트도 `np.where(isfinite)` 로 실패 처리 ✓; 출력에 (i)–(iv) 라벨 문자열이 없고 머리말 `REPORT-ONLY` ✓.

7. **문구.** §1 "보고 전용", "새 판정 라벨을 만들지 않는다", §2 원고 범위, §3 "적중/빗나감만", §6 추가만, 다중성 해당 없음 — 서로 모순 없음 ✓. 작성 시점 공개는 정직하다 (SNR 부분집합은 원 실패 수를 본 뒤 골랐지만 등록 판정에는 손대지 않음) ✓. 머리말 시각 22:50 CDT = 커밋 9356aca5 12:50:08 KST ✓. WORK_QUEUE 3b 의 "새 시행 2560 이후" 보다 10000 시작이 낫다 (dev·P3·A1C5 와 겹치지 않음) ✓.

8. **`HISNR_SKIP0` 튜플 추가와 `eval_accept --skip0` 기본 0** 은 기존 호출 (`--skip0` 없이) 의 동작을 바꾸지 않는다 — `plan` 이 `0 + 40k` 로 같고, 오프셋 규칙은 C.2 ✓.

---

집계: 반드시 6 · 권고 8 · 확인 8.
