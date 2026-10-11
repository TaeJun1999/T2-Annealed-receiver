# NEXT_EXPERIMENTS_FIGHSROOM16e4 — Sionna RT 방 그림(prior SRB)의 고SNR 점을 새 시행 n = 20480 으로 (범례 11 곡선; +6..+15 dB; **보고 전용**, 등록 v2)

- 작성: 2026-10-11 16:44 CDT, Claude Code (Opus 5.5), 초안 v1 (커밋 1404d315) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-11/review_FIGHSROOM16e4.md`: MUST 1 · SHOULD 3 · NIT 8 — 전부 반영, §5) → **v2 2026-10-11 16:54 CDT = 실행 커밋**(§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighsroom16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 사용자 지시(2026-10-11 CDT, 원문): "figure 가 왜 그리다 만거 같지?" · "근데 proposed 보면 6dB에서 BLER가 9 dB 보다 낮게 나오는데 좀 이상하지 않아? 다시 점검해봐" · "figure는 매끄러운 곡선이 나타나는게 좋아". 이 세션이 제시한 세 선택지(세로축만 조정 / 0 실패 점에 화살표 / 고SNR 시행을 8 배로) 가운데 사용자가 매끄러운 곡선을 택했다 → 원고 주 그림에 쓴 방식(`NEXT_EXPERIMENTS_FIGHS16e4.md`)을 Sionna RT 방 그림에 적용한다.
- **틀(새 규칙 없음)** = `NEXT_EXPERIMENTS_FIGHS16e4.md` v2 의 §1 (새 시행 10000..30479, n = 20480, chunk 40, +6 / +9 / +12 / +15 dB, 단계 C 대조 → 단계 R 실행 → `eval_accept --skip0/--points` + (f) → 집계표, 그림 merge 규칙, **보고 전용**)을 SRB 의 세 행으로 읽는다. 각 arm 의 체크포인트·적합·조정값·플래그는 `NEXT_EXPERIMENTS_ROOM16e4.md` §5 (SRB) 의 것 그대로다.
- **보고 전용**: 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부"·"멀어진다" 문장은 ROOM16e4 §6 의 것 그대로다. **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R2-ours-G (0/+3/+6), R3-bigamp (+9/+12/+15), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPSRB.txt`); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.**
- **작성 시점 공개**: 작성자와 사용자는 SRB 의 n = 2560 결과를 전부 봤다 — 고SNR 의 실패 수(예: V1 +6 / +9 / +12 / +15 dB = 3 / 4 / 0 / 0, b\* 6 / 5 / 1 / 1, genie 1 / 0 / 0 / 0; ROOM16e4 §6.4), 그림 `F21srb_col`, 그리고 고SNR 실패 블록의 사후 진단(`results/review_next/SRBB16e4_highsnr_fail.txt`: V1 의 +6 · +9 dB 실패 7 블록은 모두 최대 특이값 에너지 비중 0.82–0.94 인 채널이고 같은 블록에서 다른 arm 도 실패). 시행을 늘리는 이유는 "점이 튀어 보인다" 는 것이며, 어느 arm 에 유리한지를 보고 정한 것이 아니다. 새 시행 10000..30479 는 SRB 에서 한 번도 쓰인 적이 없다(SRB 의 모든 raw 의 최대 skip 은 2520; ALD 개발 시행은 2560..3071; 희소 조정·GB′ 는 다른 스트림). **단, 풀 prior 에서 시행 하나는 테스트 풀 52,353 쌍에서의 복원 추출이다** — 새 시행은 "새 추첨 + 새 데이터·잡음" 이지 새 채널이 아니다(SNR 당 서로 다른 쌍은 약 1.7 만 개이고 시행 0..2559 의 쌍과도 겹친다); 집계표의 Wilson 구간은 이 풀에 대한 평균 BLER 의 것이다(검토 S-2).
- **범위**: prior SRB 의 그림 한 장(범례 11 곡선). 경로 풀 SRP (PATH16e4) 는 넣지 않는다 — 그 풀의 GMM 은 씨앗 초기화라(PATH16e4 §6.8) 원고에 쓸지부터 사용자 결정이 필요하다; 쓰게 되면 같은 틀로 따로 등록한다.

---

## 1. 고정되는 것 (FIGHS16e4 v2 §1 과 다른 곳만)

| 항목 | 값 |
|---|---|
| 행 (`code/run_fighsroom16e4.sh` 의 `ROWS`, 이 순서) | **FHSRBB16e4**: `--prior SRB --cell C2 --stagec-ckpt ckpt/d2sx_SRB_N160000_a1_best.pt` (sha ed437f21af15c305, role best), b\* = gmm1024 (ll_val 97.00871495382869), arm `R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie`, 대조 기준 `raw_SRBB16e4`. **FHSPSRB**: `--sparse-file results/sparse/pick_SRB_C2.json` (sha 4c6da315c701b9d4), arm `SBL-loop SBL-pilot OMP-pilot R5-genie`, genie 재생 기준 FHSRBB16e4, 대조 기준 `raw_SPSRB`. **FHALDSRB**: `--stagec-ckpt …_best.pt --ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr.npz` (절대 경로 — meta·수용 (f) 가 이 문자열을 본다) (새 시행의 ALD 추정: `ald.py regen --set hisnr` (CPU) + `estimate --set hisnr` (GPU), 동결된 `tune_PILSRB.json` e0adb06cce792093 그대로), arm `ALD-pilot R5-genie`, genie 재생 기준 FHSRBB16e4, 대조 기준 `raw_ALDSRB`. 세 행 모두 fits `gmm_fits_D2_SRBB16e4` |
| 시행·SNR | 새 시행 10000..30479 (`common.HISNR_SKIP0`), n = 20480, chunk 40, SNR +6 / +9 / +12 / +15 dB; 수신기 CPU, 16 반복; 시행 스트림은 SRB 의 것(`common.trial_rng`, PID 13) → 테스트 풀 복원 추출(ROOM16e4 §1) |
| 스크립트 | `code/run_fighsroom16e4.sh` = `code/run_fighs16e4.sh` 에서 다음만 바꾼 것(머리말에 원문; 나머지 줄은 같다): 등록·로그 이름, `ROWS` 표, 새 실행의 전제 검사를 **이 스크립트의 태그로만** 한정(FIGHS16e4 의 `raw_FH*`·`FHC*`·`ald_*_hisnr.npz` 는 디스크에 그대로 둔다), ALD 기록(`PILSRB`: 테스트 추정 sha a3d249188f9c061a, 테스트 파일럿 sha 97a2d08640fef383), 회전 없는 ALD 행에서 `--rotation` 생략, HISNR raw 전제 삭제(재사용하는 행이 없다). 단계 C 대조(테스트 청크 0 에서 원 raw 와 비트 동일; ALD 추정기 대조)가 OK 가 아닌 행은 돌리지 않는다 |
| 수용 | FIGHS16e4 §1 그대로(스크립트): `eval_accept.py --skip0 10000 --n 20480 --points C2:6,9,12,15` (청크 계획, meta ntrain / bstar gmm1024 / ll_val, 체크포인트 sha·role, genie 재생), (f) 모든 청크의 `run|git` == HEAD, SP 행 `meta|sparse` == pick, ALD 행 `meta|ald_file`. 통과한 행만 집계표 `results/review_next/fighs_<TAG>.txt` 를 얻는다 |
| 그림 규칙 | `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= python -B ~/t2/conference/figures/paper_f21dmc.py SRB hs > ~/t2/conference/figures/records/paper_f21srbhs.txt` → **`F21srbhs_col.{pdf,png}`**: 곡선마다 −3 / 0 / +3 dB = 원 raw (n = 2560, 등록된 판정의 시행), +6 / +9 / +12 / +15 dB = `raw_FH<원 태그>` (n = 20480) — `fighs_merge.merge` (한 점 = 한 raw, 합치지 않는다; 실패 수는 집계표와 대조 assert). y 축은 `ROOM` 분기의 규칙을 **그려지는 값**에 적용((2e-4, 1.2) — 0 실패 점이 없고 모든 점·막대 끝이 2e-4 위일 때 — 아니면 (3e-5, 1.2)); 0 실패 점에서는 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표(n = 20480 에서 실패 1 건인 점의 Wilson 하한 8.6e-6 은 축 아래로 잘린다 — FIGHS16e4 와 같다). "오르는 칸"(SNR 이 오르는데 BLER 이 오르는 칸)은 한쪽 Fisher p 와 함께 기록에 적는다 — **평활화·재실행·점 삭제는 하지 않는다**. 세 행 가운데 수용되지 않은 것이 있으면 그 곡선은 n = 2560 점을 유지하고 기록·캡션에 밝힌다(`FIGHS_N2560`). ROOM16e4 의 등록 그림 `F21srb_col` (전 SNR n = 2560) 은 그대로 둔다 |
| 다중성·해석 | 새 검정 없음. 집계표의 Wilson 구간은 점별 서술이다(풀 평균 BLER). −3 / 0 / +3 dB 와 +6 dB 이상은 서로 다른 시행 집합이라는 점을 캡션에 적는다(주 그림과 같음). **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R2-ours-G (0/+3/+6), R3-bigamp (+9/+12/+15), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPSRB.txt`); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.** |
| 비용 [추정] | FHSRBB16e4 ≈ 65 분, FHSPSRB ≈ 50 분, FHALDSRB ≈ 10 분 = 새 시행 4 SNR × 20480 의 파일럿 재생성(CPU) + ALD 추정(GPU 한 장) + runner (CPU 192 워커) |

(§2 라벨·§4 현황 절은 없다 — 보고 전용이라 라벨이 없고, 현황은 §5 에 적는다; FIGHS16e4 의 §0.5 식 사전 ALD 재현 검사는 따로 하지 않고 스크립트의 단계 C 대조가 그 역할을 한다 — 대조가 OK 가 아니면 그 행은 돌지 않는다.)

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다)

1. n = 20480 에서 Proposed (V1) 의 실패 수는 +6 dB > +9 dB 이다(BLER 이 SNR 과 함께 내려간다). 채점: 실패 수 비교.
2. V1 · b\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 "오르는 칸" 이 없다(+3 → +6 dB 칸 포함).
3. +6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\* (점추정).
4. +15 dB 에서 V1 의 실패 수 ≤ 5 / 20480.
5. 세 행 모두 대조·수용 통과(`FIGHS_DONE ok=3 fail=0`).

## 5. 실행 전 기록

v2 2026-10-11 16:54 CDT (Opus 5.5). 검토(MUST 1 · SHOULD 3 · NIT 8) 반영: **M-1** baseline 판정점에 +6 dB 이상이 들어 있다는 사실과 "다시 판정하지 않는다" 를 머리말·§1 에 정정; S-1 `DECISIONS.md` 에 사용자 결정 줄; S-2 풀 prior 에서 새 시행의 뜻; S-3 그림 명령 원문; N-1 스크립트의 회전 로그 문구(`rotation ${V:-none}`; 동작 불변); N-3 절대 경로; N-5 잘리는 막대; N-6 · N-7 절 번호와 단계 C; N-8 비용 문구; N-2 · N-4 는 메모로 남김(조정 기록은 추적·clean 검사로 고정; 그림 기록의 `raw_<원 태그>` 꼬리표는 덧붙는 블록이 설명). 검토가 확인한 것: `bash -n`, 원 스크립트와의 diff = 머리말에 적은 변경뿐, 모든 sha·파일·전제(HEAD 1404d315 기준), `ald.py --set hisnr`, `eval_accept` 의 gmm1024, SP 행의 `-:-`, genie 재생, `dmimo` 의 시행 → 테스트 풀, 집계표의 `R0-pilot@1`, `hs_tag`, 그림의 y 규칙. **실행 커밋 = 이 문서를 담은 커밋**(그 뒤 `FIGHS_DONE` 까지 main 커밋 없음). 실행 시작 전 상태: `raw_FHSRBB16e4` · `raw_FHSPSRB` · `raw_FHALDSRB` · `ald_PILSRB_hisnr.npz` 없음.

## 6. 결과

(실행 뒤 채운다.)
