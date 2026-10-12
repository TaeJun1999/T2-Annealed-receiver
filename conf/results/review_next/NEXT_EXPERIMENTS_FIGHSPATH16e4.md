# NEXT_EXPERIMENTS_FIGHSPATH16e4 — Sionna RT 경로 그림(prior SRP)의 고SNR 점을 새 시행 n = 20480 으로 (범례 11 곡선; +6..+15 dB; **보고 전용**, 등록 v2)

- 작성: 2026-10-11 17:19 CDT, Claude Code (Opus 5.5), 초안 v1 (미커밋; sha256[:16] db646c32e705e356) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-11/review_FIGHSPATH16e4.md`: 그대로 실행 가능, MUST 1 · SHOULD 5 · NIT 5 — 반영 내용은 §5) → **v2 2026-10-11 18:34 CDT = 실행 커밋**(§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighspath16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 사용자 지시(2026-10-11 CDT, 원문): "figure는 매끄러운 곡선이 나타나는게 좋아" (→ SRB: `NEXT_EXPERIMENTS_FIGHSROOM16e4.md`) · "SRP 대강 그려봐. 보고 판단할게" (→ 기존 n = 2560 데이터로 세로축 아래쪽만 잘라낸 미리보기 한 장을 보냄; 새 실행 없음) · **"다 보강하는게 좋을 거 같다"**. 이 세션은 "다" 를 **Sionna RT 방 그림 둘(SRB · SRP)** 로 읽었다: 도시 풀 그림 둘은 보강할 점이 없다 — 범례 11 곡선 × 7 SNR 의 실패 수 최소가 Sionna RT 도시(`paper_f21srt.txt`) 1277 / 2560, DeepMIMO 도시(`paper_f21dmc.txt`) 611 / 2560 이고 실패 20 건 미만인 점이 0 개다(SRP · SRB 는 각각 77 점 중 32 점).
- **틀(새 규칙 없음)** = `NEXT_EXPERIMENTS_FIGHSROOM16e4.md` v2 (실행 커밋 193776a1; 그것은 `NEXT_EXPERIMENTS_FIGHS16e4.md` v2 §1 의 틀)를 prior SRP 의 세 행으로 읽는다: 새 시행 10000..30479, n = 20480, chunk 40, +6 / +9 / +12 / +15 dB, 단계 C 대조 → 단계 R 실행 → `eval_accept --skip0/--points` + (f) → 집계표, 그림 merge 규칙, **보고 전용**. 각 arm 의 체크포인트·적합·조정값·플래그는 `NEXT_EXPERIMENTS_PATH16e4.md` §5 (추가 줄 포함)의 것 그대로다. 아래에는 FIGHSROOM16e4 v2 와 **다른 곳만** 적는다.
- **보고 전용**: 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부"·"멀어진다" 문장은 PATH16e4 §6 의 것 그대로다. **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R3-bigamp (+9/+12/+15), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPSRP.txt`; SRB 와 달리 R2-ours-G 의 판정점은 −3/0/+3); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.**
- **이 풀의 GMM 캐비엇은 그대로 붙는다**: SRP 의 b\* ("kron 4096", ll_val 244.1932863626755, it_best 0) 는 EM 이 무너져 선택된 씨앗 초기화이고 잘 맞춘 GMM 이 아니다(PATH16e4 §5 · 6.1 · 6.7; Kronecker 구조가 아니다 — "kron" 은 적합 작업의 이름). 보강은 그 b\* 를 **그대로** 쓴다(다시 맞추지 않는다) — 그림의 "GMM prior" 곡선은 n 이 늘어도 그 초기화의 곡선이고, 캡션에 밝힌다.
- **작성 시점 공개**: 작성자와 사용자는 SRP 의 n = 2560 결과를 전부 봤다 — 고SNR 의 실패 수(V1 +6 / +9 / +12 / +15 dB = 4 / 0 / 0 / 0, b\* 29 / 3 / 2 / 0, genie 1 / 0 / 0 / 0; PATH16e4 §6.4)와 그림 `F21srp_col` · 미리보기. 이 초안을 쓸 때 SRB 의 보강 실행(FIGHSROOM16e4)은 도는 중이고 그 결과는 아직 아무도 보지 않았다. **v2 (실행 커밋)는 SRB 의 `FIGHS_DONE` 뒤에 만들어진다(그 전에는 main 커밋 금지). 그때 작성자가 SRB 의 n = 20480 결과를 봤는지, 봤다면 무엇을(집계표·그림·기록) 봤는지를 §5 에 적는다; §3 의 예측은 이 초안의 것이고 v2 에서 바꾸지 않는다**(예측 4 를 4a · 4b 로 나눈 것은 검토 S-2 의 채점 방식 정리이고 내용은 같다). 초안 v1 의 sha256[:16] db646c32e705e356 (mtime 2026-10-11 17:19 CDT) 과 스크립트 e51214bd1b49a16d (17:17 CDT) 는 검토 `prereg_reviews_2026-10-11/review_FIGHSPATH16e4.md` 머리말이 증언한다 — 그 시각 SRB 보강의 base 행은 1186 / 2048 청크, 집계표 없음. n = 2560 미리보기는 세션 스크래치에만 있고 저장소에 넣지 않는다. 시행을 늘리는 이유는 "곡선이 끊기고 튀어 보인다" 는 것이며, 어느 arm 에 유리한지를 보고 정한 것이 아니다. 새 시행 10000..30479 는 SRP 에서 한 번도 쓰인 적이 없다(SRP 의 raw 다섯 `raw_{SRPB16e4,SRPB16e4last,PILSRP,ALDSRP,SPSRP}` 의 최대 skip 은 2520; ALD 개발 시행은 2560..3071 (`tune_PILSRP.json` dev_skip 2560, n_dev 512); 희소 조정·GB′ 는 다른 스트림; `raw_SRP/` 는 σ 격자 단계의 빈 디렉토리). **풀 prior 에서 시행 하나는 테스트 풀(경로의 마지막 87 줄, 52,200 스냅숏)에서의 복원 추출이다** — 새 시행은 "새 추첨 + 새 데이터·잡음" 이지 새 채널이 아니다(시행 0..2559 의 스냅숏과도 겹친다); 집계표의 Wilson 구간은 이 풀에 대한 평균 BLER 의 것이다.
- **범위**: prior SRP 의 그림 한 장(범례 11 곡선). 어느 Sionna 결과를 원고에 쓸지는 사용자가 두 보강 그림을 보고 정한다 — **이것은 제시의 선택이지 결과의 선택이 아니다**: 두 그림·집계표는 어느 쪽을 고르든 모두 기록에 남고(`records/paper_f21{srb,srp}hs.txt`, `fighs_FH*.txt`), 판정·라벨은 바뀌지 않으며, 사용자가 고른 이유는 `DECISIONS.md` 에 원문으로 적는다(검토 S-5; 고르는 기준 자체는 사용자의 것이라 여기서 미리 정하지 않는다).

---

## 1. 고정되는 것 (FIGHSROOM16e4 v2 §1 과 다른 곳만)

| 항목 | 값 |
|---|---|
| 행 (`code/run_fighspath16e4.sh` 의 `ROWS`, 이 순서) | **FHSRPB16e4**: `--prior SRP --cell C2 --stagec-ckpt ckpt/d2sx_SRP_N160000_a1_best.pt` (sha ac4699c78b3e2d80, role best), b\* = kron K 4096 (ll_val 244.1932863626755), arm `R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie`, 대조 기준 `raw_SRPB16e4`. **FHSPSRP**: `--sparse-file results/sparse/pick_SRP_C2.json` (sha 6ae22a15de019833), arm `SBL-loop SBL-pilot OMP-pilot R5-genie`, genie 재생 기준 FHSRPB16e4, 대조 기준 `raw_SPSRP`. **FHALDSRP**: `--stagec-ckpt …_best.pt --ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr.npz` (절대 경로) (새 시행의 ALD 추정: `ald.py regen --set hisnr` (CPU) + `estimate --set hisnr` (GPU), 동결된 `tune_PILSRP.json` 858087f53952bcbf 그대로), arm `ALD-pilot R5-genie`, genie 재생 기준 FHSRPB16e4, 대조 기준 `raw_ALDSRP`. 세 행 모두 fits `gmm_fits_D2_SRPB16e4` |
| 시행·SNR | FIGHSROOM16e4 와 같다; 시행 스트림은 SRP 의 것(`common.trial_rng`, PID 15) → 테스트 풀 복원 추출(PATH16e4 §1) |
| 스크립트 | `code/run_fighspath16e4.sh` = `code/run_fighsroom16e4.sh` 에서 다음만 바꾼 것(머리말에 원문; 나머지 줄은 같다): 등록·로그 이름(`logs/run_fighspath16e4.log`), `ROWS` 표(위), 이 스크립트 행들의 태그 이름, ALD 기록(`PILSRP`: 테스트 추정 sha ebb14a8952f0ae17, 테스트 파일럿 sha 8bfc83a43f790bbf). `sed 's/SRB/SRP/g' run_fighsroom16e4.sh` 와의 차이는 머리말 주석(2–8 행) · `ROWS` 의 체크포인트 sha / b\* (계열 kron · K 4096 · ll_val) / pick sha · 등록과 로그 파일 이름(10 행) · 집계표 머리글과 두 로그 머리글의 스크립트 이름(`run_fighsroom16e4` → `run_fighspath16e4`, `FIGHSROOM16e4 §1` → `FIGHSPATH16e4 §1`; 92 · 104 · 203 행) · ALD sha (168 행) 뿐이다(검토가 diff 로 확인). 동작이 다른 줄은 `ROWS` 와 168 행뿐이다. 단계 C 대조가 OK 가 아닌 행은 돌리지 않는다 |
| 수용 | FIGHSROOM16e4 §1 그대로(스크립트): `eval_accept.py --prior SRP --bstar kron --kron-K 4096 --ll-val 244.1932863626755 --skip0 10000 --n 20480 --points C2:6,9,12,15`, (f). 통과한 행만 집계표 `results/review_next/fighs_<TAG>.txt` 를 얻는다 |
| 그림 규칙 | `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21dmc.py SRP hs > ~/t2/conference/figures/records/paper_f21srphs.txt` → **`F21srphs_col.{pdf,png}`**: FIGHSROOM16e4 §1 의 그림 규칙 그대로(곡선마다 −3 / 0 / +3 dB = 원 raw n = 2560, +6..+15 dB = `raw_FH<원 태그>` n = 20480; y 축 `ROOM` 분기 규칙; 0 실패 점에서 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표; "오르는 칸" 은 Fisher p 와 함께 기록 — **평활화·재실행·점 삭제는 하지 않는다**; 수용되지 않은 행의 곡선은 n = 2560 유지 + 공개). 그림 스크립트의 변경은 기록 문구에 등록 이름을 prior 별로 넣는 것뿐이다(`HSREG`; SRB · SRP 의 기존 기록 `paper_f21srb.txt` · `paper_f21srp.txt` 는 바뀐 스크립트로 다시 만들어도 바이트 동일 — 확인함). PATH16e4 의 등록 그림 `F21srp_col` (전 SNR n = 2560) 은 그대로 둔다 |
| 다중성·해석 | 새 검정 없음. 머리말의 굵은 문장(판정점·다시 판정하지 않음·GMM 캐비엇)이 그대로 적용된다 |
| 순서·자원 | SRB 의 보강 실행(`run_fighsroom16e4.sh`)이 `FIGHS_DONE` 을 찍은 **뒤**에만 시작한다(CPU 192 워커를 나눠 쓰지 않는다; 그 실행 중에는 main 커밋·`conf/code` 변경 금지라 이 스크립트도 그 뒤에 `conf/code` 에 넣는다). 비용 [추정] FHSRPB16e4 ≈ 90 분(원 주 실행의 청크당 시간이 SRB 의 1.9 배 — b\* 가 4,096 성분; SRB 보강 base 행 실측 × ≈ 2), FHSPSRP ≈ 50 분(SP 청크당 시간은 SRB 와 같다), FHALDSRP ≈ 10 분(regen + GPU 추정 + 2 arm runner), 단계 C ≈ 5–8 분 — 합 ≈ 2.5 시간; v2 에서 SRB 의 실측 세 값을 §5 에 적는다. 메모리: 원 SRP 주 실행(4,096 성분 GMM arm 둘, 192 워커)이 448/448 무사였고 SP 단계는 필요 ≈ 264 GB / 가용 1028 GB |

(§2 라벨·§4 현황 절은 없다 — FIGHSROOM16e4 와 같은 이유.)

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 이 초안 시점 — SRB 의 n = 20480 결과를 보기 전)

1. n = 20480 에서 Proposed (V1) 의 실패 수는 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다. 채점: 실패 수 비교.
2. V1 · b\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 "오르는 칸" 이 없다(+3 → +6 dB 칸 포함).
3. +6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\* (점추정).
4. 두 부분을 따로 채점한다(검토 S-2 — 내용은 초안과 같다): **4a.** V1 의 +9 dB 실패 수 ≥ 1 / 20480 (곡선이 +9 dB 까지 이어진다). **4b.** V1 의 +15 dB 실패 수 ≤ 5 / 20480.
5. 세 행 모두 대조·수용 통과(`FIGHS_DONE ok=3 fail=0`).

## 5. 실행 전 기록

v2 2026-10-11 18:34 CDT (Opus 5.5). 검토(MUST 1 · SHOULD 5 · NIT 5) 반영: **M-1** `sed` 차이 문장 정정(§1 스크립트); S-1 `DECISIONS.md` 에 사용자 결정 줄(이 커밋); S-2 예측 4 를 4a · 4b 로 나눠 따로 채점(내용 불변); S-3 비용 추정을 원 실행 로그 기준으로; S-4 시점 공개 문구와 초안·스크립트의 sha (검토 머리말이 증언); S-5 "제시의 선택" 임과 두 그림이 모두 기록에 남음을 적음 — 검토가 제안한 "고르는 기준은 지면·서사" · "다른 하나는 companion" 문구는 넣지 않았다(기준과 배치는 사용자의 결정이라 작성자가 미리 정하지 않는다); N-1 캐비엇 출처; N-2 파이썬 절대 경로; N-3 커밋 순서(FIGHSROOM16e4 의 §6 전사 커밋 ed265304 가 이 커밋 **앞**); N-4 · N-5 는 메모(SRB 검토의 N-2 · N-4 상속, 회귀 아님). 검토가 확인한 것: `bash -n`, `sed` 대비 diff, `ROWS` 의 모든 값 = PATH16e4 §5 = 디스크(체크포인트·b\* kron 4096 ll_val·pick·ALD 기록·fits), `# PRE` 줄 전부, runner 의 b\* 선택(심볼릭 링크 → kron 4096), `eval_accept` 인자 세 벌, `ald.py --set hisnr` 경로, 시행 → 테스트 풀, 대조 기준 raw 의 arm 키, `hs_tag`, 그림의 비-hs 기록 바이트 동일·hs 드라이 렌더, 등록의 사실 문장들. 스크립트 `code/run_fighspath16e4.sh` sha256[:16] e51214bd1b49a16d = 검토받은 파일 그대로.

**SRB 의 n = 20480 결과를 본 것(S-4)**: 이 v2 를 쓰기 전에 SRB 의 보강 실행이 끝났고(`FIGHS_DONE ok=3 fail=0`, 10-11 18:31 CDT) 작성자는 그 집계표·그림 `F21srbhs_col`·기록을 **전부 봤으며**(FIGHSROOM16e4 §6, 커밋 ed265304) 그림은 사용자에게도 보냈다 — SRB 에서 V1 의 실패 수 / 20480 은 +6 / +9 / +12 / +15 dB = 45 / 10 / 3 / 4, 0 실패 점 없음, 예측 5 개 적중. §3 의 예측은 그것을 보기 전의 초안 그대로다(4a · 4b 분리만). SRP 의 새 시행 결과는 아무도 보지 않았다. SRB 의 실측 runner 시간: FHSRBB16e4 39.0 분 · FHSPSRB 41.6 분 · FHALDSRB 1.5 분(ALD 재생성·추정 포함 약 6 분), 전체 17:01 → 18:31 CDT.

**실행 커밋 = 이 문서를 담은 커밋**(그 뒤 `FIGHS_DONE` 까지 main 커밋 없음). 실행 시작 전 상태: `raw_FHSRPB16e4` · `raw_FHSPSRP` · `raw_FHALDSRP` · `ald_PILSRP_hisnr.npz` · FHC\*SRP 대조 파일 없음.

## 6. 결과 (기록 2026-10-11 20:37 CDT, Opus 5.5 — 전사만, 해석 없음; 이 절은 추가만 한다)

### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsroom_gen.py`; 수치는 모두 기록 파일에서 읽음)

`bash code/run_fighspath16e4.sh` **한 번**, tmux `fighspath` (세션 기록 기준 [감사 N2]), 10-11 18:34 CDT 시작(git c48ee796 = 실행 커밋; 시작 줄 하나, 재개 없음). 단계 C (관측된 시험 청크 0 의 대조) 10-11 18:38 CDT: 3 receiver control(s) OK, 1 ALD estimator control(s) OK. `FIGHS_DONE ok=3 fail=0` 10-11 20:36 CDT. ABORT · SKIP · INVALID 줄: 0 개.

| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |
|---|---|---|---|---|---|---|---|
| FHSRPB16e4 | 10-11 18:38 | 74.3 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-11 19:52 | rc=0; ACCEPT: OK -- FHSRPB16e4; ACCEPT (f): OK | c48ee796 · c28b71e6ef34d918 | CONTROL: OK |
| FHSPSRP | 10-11 19:52 | 36.9 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-11 20:30 | rc=0; ACCEPT: OK -- FHSPSRP; ACCEPT (f): OK | c48ee796 · c28b71e6ef34d918 | CONTROL: OK |
| FHALDSRP | 10-11 20:34 | 1.6 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-11 20:36 | rc=0; ACCEPT: OK -- FHALDSRP; ACCEPT (f): OK | c48ee796 · c28b71e6ef34d918 | CONTROL: OK · CONTROL-ALD: OK |

수용 파일의 (f) 줄(raw 당 청크 수 · `run|git` · pick · ald · raised):

- `(f) raw_FHSRPB16e4: 2048 chunk files, run|git ['c48ee796']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FHSPSRP: 2048 chunk files, run|git ['c48ee796']; pick results/sparse/pick_SRP_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FHALDSRP: 2048 chunk files, run|git ['c48ee796']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr.npz; raised trials per arm (= failures, report only) 0`

집계표 머리말:

- `# run_fighspath16e4 git c48ee796 raw_FHSRPB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSPATH16e4 §1); load_raw warnings 0`
- `# run_fighspath16e4 git c48ee796 raw_FHSPSRP C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSPATH16e4 §1); load_raw warnings 0`
- `# run_fighspath16e4 git c48ee796 raw_FHALDSRP C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSPATH16e4 §1); load_raw warnings 0`

### 6.2 원고 범례 11 곡선 — BLER@16 실패 수 (+6 / +9 / +12 / +15 dB; 새 시행 n = 20480 과 원 raw n = 2560)

| 곡선 (arm) | 출처 | +6 dB: k / 20480 (BLER, 95 % Wilson) | +9 dB: k / 20480 (BLER, 95 % Wilson) | +12 dB: k / 20480 (BLER, 95 % Wilson) | +15 dB: k / 20480 (BLER, 95 % Wilson) | 원 raw k / 2560 (+6 / +9 / +12 / +15) |
|---|---|---|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FHSRPB16e4 | 45 (2.20e-03, [1.64e-03, 2.94e-03]) | 7 (3.42e-04, [1.66e-04, 7.05e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 4 / 0 / 0 / 0 |
| ALD-pilot | raw_FHALDSRP | 110 (5.37e-03, [4.46e-03, 6.47e-03]) | 19 (9.28e-04, [5.94e-04, 1.45e-03]) | 3 (1.46e-04, [4.98e-05, 4.31e-04]) | 2 (9.77e-05, [2.68e-05, 3.56e-04]) | 15 / 1 / 0 / 0 |
| M-ours-bstar | raw_FHSRPB16e4 | 202 (9.86e-03, [8.60e-03, 1.13e-02]) | 33 (1.61e-03, [1.15e-03, 2.26e-03]) | 3 (1.46e-04, [4.98e-05, 4.31e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 29 / 3 / 2 / 0 |
| R2-ours-G | raw_FHSRPB16e4 | 215 (1.05e-02, [9.19e-03, 1.20e-02]) | 35 (1.71e-03, [1.23e-03, 2.38e-03]) | 4 (1.95e-04, [7.60e-05, 5.02e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 27 / 1 / 2 / 0 |
| R1-turbo | raw_FHSRPB16e4 | 521 (2.54e-02, [2.34e-02, 2.77e-02]) | 78 (3.81e-03, [3.05e-03, 4.75e-03]) | 11 (5.37e-04, [3.00e-04, 9.62e-04]) | 4 (1.95e-04, [7.60e-05, 5.02e-04]) | 60 / 6 / 6 / 0 |
| R3-bigamp | raw_FHSRPB16e4 | 3386 (1.65e-01, [1.60e-01, 1.70e-01]) | 2585 (1.26e-01, [1.22e-01, 1.31e-01]) | 2881 (1.41e-01, [1.36e-01, 1.46e-01]) | 2682 (1.31e-01, [1.26e-01, 1.36e-01]) | 410 / 298 / 356 / 332 |
| R0-pilot@1 | raw_FHSRPB16e4 | 2433 (1.19e-01, [1.14e-01, 1.23e-01]) | 639 (3.12e-02, [2.89e-02, 3.37e-02]) | 169 (8.25e-03, [7.10e-03, 9.59e-03]) | 55 (2.69e-03, [2.06e-03, 3.49e-03]) | 313 / 53 / 30 / 4 |
| SBL-loop | raw_FHSPSRP | 229 (1.12e-02, [9.83e-03, 1.27e-02]) | 40 (1.95e-03, [1.43e-03, 2.66e-03]) | 8 (3.91e-04, [1.98e-04, 7.71e-04]) | 2 (9.77e-05, [2.68e-05, 3.56e-04]) | 32 / 2 / 0 / 0 |
| SBL-pilot | raw_FHSPSRP | 298 (1.46e-02, [1.30e-02, 1.63e-02]) | 39 (1.90e-03, [1.39e-03, 2.60e-03]) | 11 (5.37e-04, [3.00e-04, 9.62e-04]) | 2 (9.77e-05, [2.68e-05, 3.56e-04]) | 33 / 2 / 0 / 0 |
| OMP-pilot | raw_FHSPSRP | 720 (3.52e-02, [3.27e-02, 3.78e-02]) | 138 (6.74e-03, [5.71e-03, 7.95e-03]) | 30 (1.46e-03, [1.03e-03, 2.09e-03]) | 9 (4.39e-04, [2.31e-04, 8.35e-04]) | 81 / 9 / 3 / 1 |
| R5-genie | raw_FHSRPB16e4 | 14 (6.84e-04, [4.07e-04, 1.15e-03]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 1 / 0 / 0 / 0 |

**GMM 캐비엇(머리말) [감사 S2]**: M-ours-bstar (그림의 GMM prior) 행은 PATH16e4 의 b\* 그대로다 — EM 이 무너져 선택된 씨앗 초기화("kron 4096", ll_val 244.1933, it_best 0)이고 잘 맞춘 GMM 이 아니다. 새 시행의 실패 수는 b\* 202 / 33 / 3 / 1, Gaussian prior (R2-ours-G) 215 / 35 / 4 / 1.

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FHSRPB16e4 [14, 1, 1, 0] · FHSPSRP [14, 1, 1, 0] · FHALDSRP [14, 1, 1, 0] → 동일.

0 실패 점 (n = 20480): M-ours-dscore-C-V1 +12 dB, M-ours-dscore-C-V1 +15 dB, R5-genie +15 dB.

그림 기록 `records/paper_f21srphs.txt` 의 '오르는 칸' (SNR 이 오를 때 BLER 이 오르는 칸, 한쪽 Fisher p; 보고만): 1 줄.
- `R3-bigamp           @16  3386/20480 2585/20480 2881/20480 2682/20480   (raw_FHSRPB16e4)   rising: +9->+12 dB p=9e-06`

### 6.3 §3 예측 채점

1. V1 의 실패 수가 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다 → **적중** (45 / 7 / 0 / 0).
2. V1 · b\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **적중** (오르는 칸의 p: M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음).
3. +6 · +9 dB 에서 실패 수 V1 ≤ b\* → **적중** (45 대 202, 7 대 33; b\* 는 씨앗 초기화 GMM — 머리말 캐비엇 [감사 S2]).
4a. V1 의 +9 dB 실패 수 ≥ 1 / 20480 → **적중** (7).
4b. V1 의 +15 dB 실패 수 ≤ 5 / 20480 → **적중** (0).
5. `FIGHS_DONE ok=3 fail=0` → **적중** (ok=3 fail=0).

### 6.4 그림과 공개 사항

- **그림** `conference/figures/F21srphs_col.{pdf,png}`, 기록 `records/paper_f21srphs.txt` (§1 의 명령 그대로, `FIGHS_DONE` 뒤): 실패 수 = 집계표(assert), y 축 (3e-05, 1.2) **[감사 N1 — 이 항목의 정리된 문장: y 축 (3e-05, 1.2) 은 0 실패 점이 셋이라 규칙의 둘째 범위다(그 밖에 2e-4 이하의 점·막대 끝 12 개; Wilson 하한 8.6e-06 인 막대 넷 — GMM prior · Gaussian prior +15 dB, Perfect CSI +9 · +12 dB — 은 축 아래로 잘린다). 0 실패 점(곡선이 거기서 끊긴다; Perfect CSI 만 `fighs_merge.zero_arrows` 화살표): Proposed (diffusion prior) +12 · +15 dB, Perfect CSI +15 dB — 제안 곡선은 +9 dB 에서 끝나고 +12 · +15 dB 에는 표시가 없다(0 / 20480, Wilson 상한 1.88e-04). 아래는 처음 적은 문장(인용이 깨져 있다)]**. 0 실패 점: fighs_merge.zero_arrows): Proposed (diffusion prior) +12 dB; Proposed (diffusion prior) +15 dB; Perfect CSI +15 dB. −3 / 0 / +3 dB 는 원 raw (n = 2560) 그대로다. **GMM prior 곡선은 PATH16e4 의 씨앗 초기화 b\* 의 곡선이다**(머리말의 캐비엇; 캡션에 밝힌다).
- 그림 스크립트 `paper_f21dmc.py` · `fighs_merge.py` 는 이 그림을 만들 때 작업 트리에 미커밋 변경이 있었다(이 §6 과 같은 커밋): hs 모드 기록 문구 한 곳("counts before the merge …"; FIGHSROOM16e4 감사 N2), 그리고 FIGHSX16e4 를 위한 `hsx` 모드(이 그림은 쓰지 않는다). `SRB hs` 를 바뀐 스크립트로 다시 돌린 PDF · PNG 가 커밋본과 바이트 동일하고 비-hs 기록(`paper_f21srb.txt` · `paper_f21srp.txt`)도 바이트 동일함을 확인했다.
- 새 시행의 ALD 추정 파일 `results/ald/ald_PILSRP_hisnr.npz` sha256[:16] 3a13dfb7191bd3ed (git 밖).
- 실행 중 main 커밋 없음(HEAD c48ee796 그대로; 스크립트의 HEAD 검사 통과). 함께 돈 것(결과 중립 — 수신기는 CPU 결정적; 세션 기록 기준): SRP 시드 a3 학습(GPU 0, 19:20 CDT 까지), SRB 시드 a2 · a3 학습(GPU 0 · 2, 19:26 CDT ~; 등록 밖, 사용자 "GPU 빈거에 뭐라도 하자"), FIGHSROOM16e4 의 기록 감사와 FIGHSX16e4 의 사전 검토(Fable 서브에이전트, CPU 3 스레드 이하, 읽기 전용 — 이 실행의 결과는 읽지 않음), SRB 의 사후 진단 한 번(CPU 2 스레드), 그림 스크립트의 회귀 확인 렌더, 한 배치 ALD 추정의 합성 입력 시험(GPU 1, FIGHSX16e4 검토 보고 뒤 약 1 분 — 이 실행의 ALD 행보다 먼저 끝남).
- 실행 중 작성자는 이 실행의 진행 줄 수(`grep -c done`)와 운영 로그만 봤고 결과 파일은 `FIGHS_DONE` 뒤에 처음 열었다(세션 기록 기준).
- §1 의 비용 추정(base ≈ 90 분 · SP ≈ 50 분 · ALD ≈ 10 분, 합 ≈ 2.5 시간) 대비 실측 runner 74.3 · 36.9 · 1.6 분, 전체 10-11 18:34 → 10-11 20:36 CDT.
- 기록 감사(Fable)는 이 절을 쓴 뒤에 받는다 — 결과는 추가 줄로 적는다.

### 6.5 기록 감사 (Fable 5.1 서브에이전트, 보고서 파일 mtime 2026-10-11 21:00 CDT; `prereg_audit_2026-10-11/audit_FIGHSPATH16e4.md`, 재계산 `recompute_fighspath.py` → `.out`, 등록 도구 재실행 `rerun_fighspath_accept_FH*.txt`)

감사 대상 = 커밋 aefbfc12 (§6 과, 같은 커밋의 `docs/EXPERIMENTS.md` 마지막 행·70 · 72 행의 정정, FIGHSROOM16e4 §6.5 · 6.6, ROOM16e4 의 [정정], `audit_ROOM16e4.md` 의 정정 줄, `DECISIONS.md` 한 줄). **이 문서 §6.1–6.4 의 수치·채점·인용 오류 0**: 자체 판독기로 새 raw 3 × 2048 청크(시행 10000..30479 를 SNR 당 한 번씩; 모든 청크 `run|git` c48ee796, `+dirty` 없음)·원 raw·대조 raw·ALD npz 를 직접 읽음(검사 묶음 63 개 중 62 통과; 나머지 하나는 아래 N3). meta (kron / K 4096 / ll_val 244.1932863626755, 체크포인트 ac4699c78b3e2d80), SP 의 `meta|sparse` == pick, ALD 의 `meta|ald_file`, genie 세 raw 비트 동일(14 / 1 / 1 / 0), 대조 비교 0 다름, 집계표 56 행과 Wilson 문자열, 6.2 의 44 칸과 원 raw 열, 0 실패 점 셋, 오르는 칸 하나(BiG-AMP +9 → +12 dB, p 9e-06), 예측 여섯의 채점, 시각표(시작 줄 하나, 실행 중 커밋 없음) 일치; `eval_accept` 세 행 재실행 → `ACCEPT: OK`; 생성기 `s6_fighsroom_gen.py SRP` 재실행이 6.1–6.3 과 바이트 동일; `paper_f21dmc.py` 를 커밋된 코드로 `SRP hs` · `SRB hs` · `SRP` · `SRB` 다시 그린 기록 4 개·PDF/PNG 8 개가 커밋본과 **바이트 동일**.

**MUST 0 · SHOULD 2 · NIT 8 — 모두 반영(이 문서의 수치·채점 불변; 기록 2026-10-11 21:02 CDT, Opus 5.5)**: **S1** (다른 문서) FIGHSROOM16e4 §6.6 의 "시행" 번호가 새 raw 안의 위치였다 — 스트림 시행 번호(= 10000 + 위치)로 정정(제자리 표시), 진단 스크립트가 스트림 번호를 찍도록 고치고 파일을 다시 만듦. **S2** GMM 캐비엇을 6.2 의 표 뒤와 6.3 의 3 번에 붙임(제자리). N1 6.4 첫 항목의 정리된 문장(y 축 범위의 이유, 제안 곡선이 +9 dB 에서 끝남, 잘리는 막대 넷) — 제자리; N2 "tmux `fighspath`" 는 세션 기록 기준; N3 · N4 · N5 · N8 (다른 문서) FIGHSROOM16e4 §6.4 의 1.46e-04 · 1.95e-04, §6.5 의 `DECISIONS.md` 줄 지칭과 "확인하지 못한 것" 한 항목, §6.6 의 지문 두 개; N6 (다른 문서) `DECISIONS.md` 10:38 KST 줄의 "SRP 시드 a2 · a3 는 19:20 CDT 에 끝남" → a2 는 16:47 CDT, a3 는 19:20 CDT (정정 줄 추가); N7 `docs/EXPERIMENTS.md` 의 이 실험 행에 오르는 칸과 0 실패 점을 이름으로 적음. 감사가 확인하지 못한 것: 세션 기록 기준 진술(tmux 이름, 회귀 렌더, 결과 파일을 처음 연 시점, 병행 작업의 스레드 수, GPU 1 의 합성 ALD 시험), 사용자 인용, 스크래치 `srb_seeds.sh`, 진단 파일의 특이값 비중·지문(실패 위치·반복별 수·함께 실패한 arm 은 raw 에서 확인), 풀 통계의 원 재계산, `DECISIONS.md` 의 'GPU 3 · 4 · 5 는 컨테이너 밖 프로세스가 점유'(실행 당시), `highsnr_fail_SRB.py` 기본 모드 출력의 재실행(diff 로만 판단) [FIGHSX16e4 감사 N6].
