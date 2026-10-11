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

## 6. 결과

(실행 뒤 채운다.)
