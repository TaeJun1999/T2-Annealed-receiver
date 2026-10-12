# NEXT_EXPERIMENTS_FIGHSDMI16e4 — DeepMIMO 실내 그림(prior DMI)의 고SNR 점을 새 시행 n = 20480 으로 (범례 11 곡선; +6..+15 dB; **보고 전용**, 초안 v1)

- 작성: 2026-10-12 18:25 CDT, Claude Code (Opus 5.5), 초안 v1 (미커밋) → 적대적 검토(Fable 서브에이전트; `prereg_reviews_2026-10-11/review_FIGHSDMI16e4.md`) → v2 = 실행 커밋(§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighsdmi16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 사용자 지시(2026-10-11 CDT, 원문): "figure는 매끄러운 곡선이 나타나는게 좋아" (→ SRB: `NEXT_EXPERIMENTS_FIGHSROOM16e4.md`) · "다 보강하는게 좋을 거 같다" (→ SRP: `NEXT_EXPERIMENTS_FIGHSPATH16e4.md`). **DMI 에 대한 별도 지시는 없다 — 이 세션의 해석**: 그 두 지시는 "BLER 이 낮아 고SNR 점이 몇 건 / 0 건인 방 풀 그림" 에 대한 것이었고, 10-12 CDT 에 되돌려 실행한 DMI 의 그림 `F21dmi_col` 이 같은 상태다(범례 11 곡선 × 7 SNR = 77 점 가운데 0 실패 18 점, 제안 곡선은 +9 dB 부터 0 실패 — `records/paper_f21dmi.txt`; ROOM16e4 §7.4). 그림은 10-12 CDT 에 baseline 이 끝난 뒤(`DMI_BASE_DONE` 18:15 CDT) 사용자에게 보냈고 보강을 준비 중이라고 알렸다. 사용자가 원하지 않으면 실행 전·중 어느 때든 멈춘다.
- **틀(새 규칙 없음)** = `NEXT_EXPERIMENTS_FIGHSPATH16e4.md` v2 (실행 커밋 c48ee796) = `NEXT_EXPERIMENTS_FIGHSROOM16e4.md` v2 (193776a1) = `NEXT_EXPERIMENTS_FIGHS16e4.md` v2 §1 의 틀을 prior DMI 의 세 행으로 읽는다: 새 시행 10000..30479, n = 20480, chunk 40, +6 / +9 / +12 / +15 dB, 단계 C 대조 → 단계 R 실행 → `eval_accept --skip0/--points` + (f) → 집계표, 그림 merge 규칙, **보고 전용**. 각 arm 의 체크포인트·적합·조정값·플래그는 `NEXT_EXPERIMENTS_ROOM16e4.md` 5-DMI 의 것 그대로다. 아래에는 FIGHSPATH16e4 v2 와 **다른 곳만** 적는다.
- **보고 전용**: 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부"·"멀어진다" 문장은 ROOM16e4 §7 의 것 그대로다. **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R3-bigamp (+6/+9/+12), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPDMI.txt`; R2-ours-G 의 판정점은 −3/0/+3); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.**
- **GMM**: DMI 의 b\* 는 정상 수렴한 full 공분산 K = 1024 (ll_val 112.04253042212595; 격자 끝 캐비엇 — ROOM16e4 5-DMI · §7.1). 보강은 그 b\* 를 그대로 쓴다(다시 맞추지 않는다).
- **작성 시점 공개**: 작성자와 사용자는 DMI 의 n = 2560 결과를 전부 봤다 — 고SNR 의 실패 수(V1 +6 / +9 / +12 / +15 dB = 4 / 0 / 0 / 0, b\* 7 / 0 / 0 / 0, genie 0 / 0 / 0 / 0; ROOM16e4 §7.4)와 그림 `F21dmi_col`. Sionna 방 두 풀의 보강 결과(n = 20480 의 +6 / +9 / +12 / +15 dB: SRB V1 45 / 10 / 3 / 4, SRP V1 45 / 7 / 0 / 0; n = 81920 의 +12 / +15 dB: SRB 12 / 11, SRP 4 / 1 — FIGHSROOM · FIGHSPATH · FIGHSX16e4 §6)도 전부 봤다. DMI 의 새 시행 결과는 아무도 보지 않았다(`raw_FH*DMI*` · `ald_PILDMI_hisnr.npz` 없음). 시행을 늘리는 이유는 "곡선이 끊겨 보인다" 는 것이며 어느 arm 에 유리한지를 보고 정한 것이 아니다. 새 시행 10000..30479 는 DMI 에서 한 번도 쓰인 적이 없다(DMI 의 raw 다섯 `raw_{DMIB16e4,DMIB16e4last,PILDMI,ALDDMI,SPDMI}` 의 최대 skip 은 2520; ALD 개발 시행은 2560..3071 (`tune_PILDMI.json` dev_skip 2560, n_dev 512); 희소 조정·GB′ 는 다른 스트림; `raw_DMI/` 는 σ 격자 단계의 빈 디렉토리). **풀 prior 에서 시행 하나는 테스트 풀(60,700 쌍)에서의 복원 추출이다** — 새 시행은 "새 추첨 + 새 데이터·잡음" 이지 새 채널이 아니다(시행 0..2559 의 쌍과도 겹칠 수 있다); 집계표의 Wilson 구간은 이 풀에 대한 평균 BLER 의 것이다.
- **범위**: prior DMI 의 그림 한 장(범례 11 곡선). 어느 결과·그림을 원고에 쓸지는 사용자가 정한다(제시의 선택이지 결과의 선택이 아니다 — 두 그림 `F21dmi_col` · `F21dmihs_col` 과 집계표는 모두 기록에 남고 판정·라벨은 바뀌지 않는다).

---

## 1. 고정되는 것 (FIGHSPATH16e4 v2 §1 과 다른 곳만)

| 항목 | 값 |
|---|---|
| 행 (`code/run_fighsdmi16e4.sh` 의 `ROWS`, 이 순서) | **FHDMIB16e4**: `--prior DMI --cell C2 --stagec-ckpt ckpt/d2sx_DMI_N160000_a1_best.pt` (sha dc784649f1e9b890, role best), b\* = `gmm1024` (full K 1024, ll_val 112.04253042212595), arm `R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie`, 대조 기준 `raw_DMIB16e4`. **FHSPDMI**: `--sparse-file results/sparse/pick_DMI_C2.json` (sha 8f72c113efb91b0b), arm `SBL-loop SBL-pilot OMP-pilot R5-genie`, genie 재생 기준 FHDMIB16e4, 대조 기준 `raw_SPDMI`. **FHALDDMI**: `--stagec-ckpt …_best.pt --ald-file /home/HTJ/t2/conf/results/ald/ald_PILDMI_hisnr.npz` (절대 경로) (새 시행의 ALD 추정: `ald.py regen --set hisnr` (CPU) + `estimate --set hisnr` (GPU), 동결된 `tune_PILDMI.json` 1e7824c1bae10376 그대로), arm `ALD-pilot R5-genie`, genie 재생 기준 FHDMIB16e4, 대조 기준 `raw_ALDDMI`. 세 행 모두 fits `gmm_fits_D2_DMIB16e4` |
| 시행·SNR | FIGHSROOM16e4 와 같다; 시행 스트림은 DMI 의 것(`common.trial_rng`, PID 14) → 테스트 풀 복원 추출(ROOM16e4 §1) |
| 스크립트 | `code/run_fighsdmi16e4.sh` (sha256[:16] 8970b917fed6f67d) = `code/run_fighspath16e4.sh` 에서 다음만 바꾼 것(머리말에 원문): 등록·로그 이름(`logs/run_fighsdmi16e4.log`), `ROWS` 표(위), 이 스크립트 행들의 태그 이름, ALD 기록(`PILDMI`: 테스트 추정 sha b0145dac7b7076aa, 테스트 파일럿 sha 1e8cc99169b3f18c), **그리고 한 줄 추가(`# EARLY`)**. `sed 's/SRP/DMI/g; s/fighspath/fighsdmi/g; s/FIGHSPATH/FIGHSDMI/g' run_fighspath16e4.sh` 와의 차이는 머리말 주석(2–10 행) · `ROWS` 의 체크포인트 sha / b\* (계열 gmm1024 · kron K `-` · ll_val) / pick sha (20–22 행) · ALD sha (171 행) · 추가 줄(195 행)뿐이다. **`# EARLY` 줄**: 단계 C 가 끝난 직후, ALD 행의 새 시행 추정(`ald_new` = `ald.py regen --set hisnr` + `estimate --set hisnr`)을 **먼저** 만든다 — 공유 서버에서 빈 GPU 를 몇 시간 잡아 둘 수 없어서다(FIGHSX16e4 는 마지막 행에서 "no free GPU" 로 한 번 재개했다). 단계 R 의 같은 `ald_new` 는 이 HEAD 에서 만든 추정 파일을 찾아 그대로 쓴다(재개 때의 기존 분기; 파일의 prov git = HEAD 일 때만). 추정은 조정 기록·파일럿·체크포인트·고정 시드로 정해지므로(단계 C 의 ALD 추정기 대조가 비트 동일성을 본다) 언제 만들어도 같은 파일이고 수치는 바뀌지 않는다. 그때 빈 GPU 가 없으면 로그에 줄을 남기고 넘어가며 단계 R 이 한 번 더 시도한다. 단계 C 대조가 OK 가 아닌 행은 돌리지 않는다 |
| 수용 | FIGHSROOM16e4 §1 그대로(스크립트): `eval_accept.py --prior DMI --bstar gmm1024 --ll-val 112.04253042212595 --skip0 10000 --n 20480 --points C2:6,9,12,15`, (f). 통과한 행만 집계표 `results/review_next/fighs_<TAG>.txt` 를 얻는다 |
| 그림 규칙 | `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21dmc.py DMI hs > ~/t2/conference/figures/records/paper_f21dmihs.txt` → **`F21dmihs_col.{pdf,png}`**: FIGHSROOM16e4 §1 의 그림 규칙 그대로(곡선마다 −3 / 0 / +3 dB = 원 raw n = 2560, +6..+15 dB = `raw_FH<원 태그>` n = 20480; y 축 `ROOM` 분기 규칙; 0 실패 점에서 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표; "오르는 칸" 은 Fisher p 와 함께 기록 — **평활화·재실행·점 삭제는 하지 않는다**; 수용되지 않은 행의 곡선은 n = 2560 유지 + 공개). 그림 스크립트의 변경은 `HSREG` 에 `"DMI": "FIGHSDMI16e4"` 를 넣는 것뿐이다(기존 기록 `paper_f21dmi.txt` · `paper_f21srb.txt` · `paper_f21srbhs.txt` 와 그 PDF 는 바뀐 스크립트로 다시 만들어도 바이트 동일 — 확인함). ROOM16e4 의 등록 그림 `F21dmi_col` (전 SNR n = 2560) 은 그대로 둔다 |
| 다중성·해석 | 새 검정 없음. 머리말의 굵은 문장(판정점·다시 판정하지 않음)이 그대로 적용된다 |
| 순서·자원 | 다른 등록 runner 가 돌지 않을 때만 시작한다(지금 없음). **CPU 96 스레드**: `taskset -c 24-47,120-143,72-95,168-191 bash code/run_fighsdmi16e4.sh` (사용자 지시 10-12 CDT; runner 는 192 워커를 만들어 96 스레드를 나눠 쓴다 — 결과 불변). 함께 도는 것: ROOM16e4 §7 의 기록 감사(Fable 서브에이전트; CPU 16 스레드 이하, NUMA 노드 0; raw 를 읽기만 한다 — 감사의 반영은 `FIGHS_DONE` 뒤에 커밋한다). 비용 [추정] FHDMIB16e4 ≈ 65 분(SRB 보강 base 행 39.0 분 × DMI / SRB 주 실행 시간비 46.6 / 28.3), FHSPDMI ≈ 60 분(41.6 분 × 14.9 / 10.4), FHALDDMI ≈ 5 분, 단계 C + 이른 ALD 추정 ≈ 10–15 분 — 합 ≈ 2.5 시간. 메모리: SP 단계 필요 ≈ 264 GB / 가용 ≈ 1040 GB (ROOM16e4 §7.3) |

(§2 라벨·§4 현황 절은 없다 — FIGHSROOM16e4 와 같은 이유.)

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 이 초안 시점 — DMI 의 n = 20480 결과를 보기 전, Sionna 방 두 풀의 보강 결과는 본 뒤)

1. n = 20480 에서 Proposed (V1) 의 실패 수는 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다. 채점: 실패 수 비교.
2. V1 · b\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 "오르는 칸" 이 없다(+3 → +6 dB 칸 포함).
3. +6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\* (점추정).
4. 두 부분을 따로 채점한다: **4a.** V1 의 +9 dB 실패 수 ≥ 1 / 20480 (곡선이 +9 dB 까지 이어진다). **4b.** V1 의 +15 dB 실패 수 ≤ 5 / 20480.
5. 세 행 모두 대조·수용 통과(`FIGHS_DONE ok=3 fail=0`), 재개 없이 한 번에.
6. (예측이 아니라 미리 적는 가능성) n = 2560 에서 V1 의 +6 dB 가 4 건, +9 dB 부터 0 건이었으므로 n = 20480 에서도 V1 의 +12 · +15 dB 가 0 건일 수 있다 — 그러면 곡선은 그 점에서 끊긴 채로 그리고(규칙대로), +12 / +15 dB 를 n = 81920 으로 다시 재는 것(FIGHSX16e4 의 틀)은 사용자가 그림을 보고 정한다.

## 5. 실행 전 기록

(v2 에서 채운다: 검토 반영, 스크립트 sha, 실행 직전 상태.)
