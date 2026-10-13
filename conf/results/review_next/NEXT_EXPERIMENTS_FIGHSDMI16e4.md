# NEXT_EXPERIMENTS_FIGHSDMI16e4 — DeepMIMO 실내 그림(prior DMI)의 고SNR 점을 새 시행 n = 20480 으로 (범례 11 곡선; +6..+15 dB; **보고 전용**, 등록 v2)

- 작성: 2026-10-12 18:25 CDT, Claude Code (Opus 5.5), 초안 v1 (미커밋; sha256[:16] f45e7127c24913b3) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-11/review_FIGHSDMI16e4.md`: 수정 후 실행 가능, MUST 1 · SHOULD 5 · NIT 8 — 반영 내용은 §5) → **v2 2026-10-12 18:43 CDT = 실행 커밋**(§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighsdmi16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 사용자 지시(2026-10-11 CDT, 원문): "figure는 매끄러운 곡선이 나타나는게 좋아" (→ SRB: `NEXT_EXPERIMENTS_FIGHSROOM16e4.md`) · "다 보강하는게 좋을 거 같다" (→ SRP: `NEXT_EXPERIMENTS_FIGHSPATH16e4.md`). **DMI 에 대한 별도 지시는 없다 — 이 세션의 해석**: 그 두 지시는 BLER 이 낮아 고SNR 점이 몇 건 / 0 건인 방 풀 그림에 대한 것이었고, 10-12 CDT 에 되돌려 실행한 DMI 의 그림 `F21dmi_col` 이 같은 상태다(범례 11 곡선 × 7 SNR = 77 점 가운데 0 실패 18 점, 제안 곡선은 +9 dB 부터 0 실패 — `records/paper_f21dmi.txt`; ROOM16e4 §7.4). 그림은 10-12 CDT 에 baseline 이 끝난 뒤(`DMI_BASE_DONE` 18:15 CDT) 사용자에게 보냈고 보강을 준비 중이라고 알렸다. **사용자의 확인은 받지 않았다 — 알리기만 했다**(§5). 사용자가 원하지 않으면 실행 전·중 어느 때든 멈춘다.
- **틀(새 규칙 없음)** = `NEXT_EXPERIMENTS_FIGHSPATH16e4.md` v2 (실행 커밋 c48ee796) = `NEXT_EXPERIMENTS_FIGHSROOM16e4.md` v2 (193776a1) = `NEXT_EXPERIMENTS_FIGHS16e4.md` v2 §1 의 틀을 prior DMI 의 세 행으로 읽는다: 새 시행 10000..30479, n = 20480, chunk 40, +6 / +9 / +12 / +15 dB, 단계 C 대조 → 단계 R 실행 → `eval_accept --skip0/--points` + (f) → 집계표, 그림 merge 규칙, **보고 전용**. 각 arm 의 체크포인트·적합·조정값·플래그는 `NEXT_EXPERIMENTS_ROOM16e4.md` 5-DMI 의 것 그대로다. 아래에는 FIGHSPATH16e4 v2 와 **다른 곳만** 적는다.
- **보고 전용**: 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부"·"멀어진다" 문장은 ROOM16e4 §7 의 것 그대로다. **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 16 개의 판정점은 앵커별이라 R0-pilot@1 (+3/+6/+9), R1-turbo (0/+3/+6), R3-bigamp (+6/+9/+12), R4-llr (+9/+12/+15), R4-scvamp (+3/+6/+9), OMP-pilot (0/+3/+6) 은 +6 dB 이상을 포함한다 (`pairB_SPDMI.txt`; R2-ours-G 의 판정점은 −3/0/+3); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6..+15 dB 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.**
- **GMM**: DMI 의 b\* 는 full 공분산 K = 1024 (ll_val 112.04253042212595; EM 이 초기화에서 멈춘 SRP 와 달리 it_best 70 / n_iter 72 에서 선택; **격자 끝 캐비엇 + 수렴 캐비엇(재시드 6,847)** — ROOM16e4 5-DMI · §7.1). 보강은 그 b\* 를 그대로 쓴다(다시 맞추지 않는다).
- **작성 시점 공개**: 작성자와 사용자는 DMI 의 n = 2560 결과를 전부 봤다 — 고SNR 의 실패 수(V1 +6 / +9 / +12 / +15 dB = 4 / 0 / 0 / 0, b\* 7 / 0 / 0 / 0, genie 0 / 0 / 0 / 0; ROOM16e4 §7.4)와 그림 `F21dmi_col`. **n = 2560 그림에서 점추정으로 제안 곡선 이하인 baseline 점 12 개**(ROOM16e4 §7.4 의 목록; 양쪽이 0 실패가 아닌 것은 Annealed Langevin +6 dB 의 4 대 4 하나, 나머지 11 개는 양쪽 0 실패)도 봤다 — 그 점들이 바로 이 보강이 다시 재서 그리는 점들이다(보강 그림 기록의 'at or below the proposed curve' 줄을 §6 에 원문으로 옮긴다). Sionna 방 두 풀의 보강 결과(n = 20480 의 +6 / +9 / +12 / +15 dB: SRB V1 45 / 10 / 3 / 4, SRP V1 45 / 7 / 0 / 0; n = 81920 의 +12 / +15 dB: SRB 12 / 11, SRP 4 / 1 — FIGHSROOM · FIGHSPATH · FIGHSX16e4 §6)도 전부 봤다. DMI 의 새 시행 결과는 아무도 보지 않았다(`raw_FH*DMI*` · `ald_PILDMI_hisnr.npz` 없음). 시행을 늘리는 이유는 "곡선이 끊겨 보인다" 는 것이며 어느 arm 에 유리한지를 보고 정한 것이 아니다. 새 시행 10000..30479 는 DMI 에서 한 번도 쓰인 적이 없다(DMI 의 raw 다섯 `raw_{DMIB16e4,DMIB16e4last,PILDMI,ALDDMI,SPDMI}` 의 최대 skip 은 2520; ALD 개발 시행은 2560..3071 (`tune_PILDMI.json` dev_skip 2560, n_dev 512); 희소 조정·GB′ 는 다른 스트림; `raw_DMI/` 는 σ 격자 단계의 빈 디렉토리). **풀 prior 에서 시행 하나는 테스트 풀(60,700 쌍)에서의 복원 추출이다** — 새 시행은 "새 추첨 + 새 데이터·잡음" 이지 새 채널이 아니다(시행 0..2559 의 쌍과도 겹친다 — SNR 당 20480 번 추출에서 서로 다른 쌍의 기대값 약 17,400, 시행 0..2559 가 뽑은 쌍을 다시 뽑는 시행 약 850; 검토 N-3 의 계산); 집계표의 Wilson 구간은 이 풀에 대한 평균 BLER 의 것이다.
- **범위**: prior DMI 의 그림 한 장(범례 11 곡선). 어느 결과·그림을 원고에 쓸지는 사용자가 정한다(제시의 선택이지 결과의 선택이 아니다 — 두 그림 `F21dmi_col` · `F21dmihs_col` 과 집계표는 모두 기록에 남고 판정·라벨은 바뀌지 않는다).

---

## 1. 고정되는 것 (FIGHSPATH16e4 v2 §1 과 다른 곳만)

| 항목 | 값 |
|---|---|
| 행 (`code/run_fighsdmi16e4.sh` 의 `ROWS`, 이 순서) | **FHDMIB16e4**: `--prior DMI --cell C2 --stagec-ckpt ckpt/d2sx_DMI_N160000_a1_best.pt` (sha dc784649f1e9b890, role best), b\* = `gmm1024` (full K 1024, ll_val 112.04253042212595), arm `R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie`, 대조 기준 `raw_DMIB16e4`. **FHSPDMI**: `--sparse-file results/sparse/pick_DMI_C2.json` (sha 8f72c113efb91b0b), arm `SBL-loop SBL-pilot OMP-pilot R5-genie`, genie 재생 기준 FHDMIB16e4, 대조 기준 `raw_SPDMI`. **FHALDDMI**: `--stagec-ckpt …_best.pt --ald-file /home/HTJ/t2/conf/results/ald/ald_PILDMI_hisnr.npz` (절대 경로) (새 시행의 ALD 추정: `ald.py regen --set hisnr` (CPU) + `estimate --set hisnr` (GPU), 동결된 `tune_PILDMI.json` 1e7824c1bae10376 그대로), arm `ALD-pilot R5-genie`, genie 재생 기준 FHDMIB16e4, 대조 기준 `raw_ALDDMI`. 세 행 모두 fits `gmm_fits_D2_DMIB16e4` |
| 시행·SNR | FIGHSROOM16e4 와 같다; 시행 스트림은 DMI 의 것(`common.trial_rng`, PID 14) → 테스트 풀 복원 추출(ROOM16e4 §1) |
| 스크립트 | `code/run_fighsdmi16e4.sh` (sha256[:16] b32cfd92db26e8e3; 검토받은 초안 8970b917fed6f67d 에 검토 M-1 · S-3 · N-1 을 반영한 것) = `code/run_fighspath16e4.sh` 에서 다음만 바꾼 것(머리말에 원문): 등록·로그 이름(`logs/run_fighsdmi16e4.log`), `ROWS` 표(위), 이 스크립트 행들의 태그 이름, ALD 기록(`PILDMI`: 테스트 추정 sha b0145dac7b7076aa, 테스트 파일럿 sha 1e8cc99169b3f18c), **그리고 한 줄 추가(`# EARLY`)와 주석 한 줄**. `sed 's/SRP/DMI/g; s/fighspath/fighsdmi/g; s/FIGHSPATH/FIGHSDMI/g' run_fighspath16e4.sh` 와의 차이(`diff` 머리줄 `2,7c2,11` · `17,19c21,23` · `138c142` · `168c172` · `191a196`)는 머리말 주석(2–11 행) · `ROWS` 의 체크포인트 sha / b\* (계열 gmm1024 · kron K `-` · ll_val) / pick sha (21–23 행) · `ald_new` 안의 주석 한 줄(142 행; 동작 없음) · ALD sha (172 행) · 추가 줄(196 행)뿐이다. 동작이 다른 줄은 `ROWS` · 172 행 · 196 행이다. **`# EARLY` 줄**: 단계 C 가 끝난 직후, ALD 행의 새 시행 추정(`ald_new` = `ald.py regen --set hisnr` + `estimate --set hisnr`)을 **먼저** 만든다 — **그 행의 두 대조(`CONTROL: OK` · `CONTROL-ALD: OK`)가 모두 OK 일 때만**(검토 M-1: 단계 R 의 관문과 같은 두 줄; 기준 행 FHDMIB16e4 의 수용은 그때 아직 없어 보지 않는다 — 기준 행이 수용되지 않으면 추정 파일만 남고 ALD 행은 돌지 않는다). 이유: 공유 서버에서 빈 GPU 를 몇 시간 잡아 둘 수 없다(FIGHSX16e4 는 마지막 행이 "no free GPU" 로 멈춰 재개 시도가 세 번 들었다 — FIGHSX16e4 §6.4). 단계 R 의 같은 `ald_new` 는 이 HEAD 에서 만든 추정 파일을 찾아 그대로 쓴다(재개 때의 기존 분기; 파일의 prov git = HEAD 일 때만). 추정은 조정 기록·파일럿·체크포인트·고정 시드로 정해진다(`ald.py` 의 결정적 설정과 `estimate` 안의 같은 시드 두 번 실행 assert; 단계 C 의 추정기 대조는 시험 배치 2560 만 본다 — 검토 N-6) — 같은 HEAD · 같은 GPU 기종에서는 언제 만들어도 같은 파일이고 수치는 바뀌지 않는다. 그때 빈 GPU 가 없으면 `ald_new` 가 로그에 `ABORT: no free GPU …` 줄을 남기고 넘어가며 단계 R 이 한 번 더 시도한다 — **이 ABORT 줄은 행의 실패가 아니다**(예측 5 는 시작 줄 1 개 + `ok=3 fail=0` 으로 채점한다; 검토 N-2). **재개할 때**: 기준 행에 기대는 행은 기준 행과 함께 준다(`--resume FHDMIB16e4 FHALDDMI`, 또는 태그 없이 `--resume`; 혼자 주면 "genie reference not accepted" 로 SKIP — 검토 S-2). 상속 메모(검토 N-8, 회귀 아님): ALD 조정 기록의 sha 는 `case` 줄이 보지 않고 추적·clean 만 본다. 단계 C 대조가 OK 가 아닌 행은 돌리지 않는다 |
| 수용 | FIGHSROOM16e4 §1 그대로(스크립트): `eval_accept.py --prior DMI --bstar gmm1024 --ll-val 112.04253042212595 --skip0 10000 --n 20480 --points C2:6,9,12,15`, (f). 통과한 행만 집계표 `results/review_next/fighs_<TAG>.txt` 를 얻는다 |
| 그림 규칙 | `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21dmc.py DMI hs > ~/t2/conference/figures/records/paper_f21dmihs.txt` → **`F21dmihs_col.{pdf,png}`**: FIGHSROOM16e4 §1 의 그림 규칙 그대로(곡선마다 −3 / 0 / +3 dB = 원 raw n = 2560, +6..+15 dB = `raw_FH<원 태그>` n = 20480; y 축 `ROOM` 분기 규칙; 0 실패 점에서 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표; "오르는 칸" 은 Fisher p 와 함께 기록 — **평활화·재실행·점 삭제는 하지 않는다**; 수용되지 않은 행의 곡선은 n = 2560 유지 + 공개). 그림 스크립트의 변경은 `HSREG` 에 `"DMI": "FIGHSDMI16e4"` 를 넣는 것뿐이다(기존 기록 `paper_f21dmi.txt` · `paper_f21srb.txt` · `paper_f21srbhs.txt` 와 그 PDF 는 바뀐 스크립트로 다시 만들어도 바이트 동일 — 확인함). ROOM16e4 의 등록 그림 `F21dmi_col` (전 SNR n = 2560) 은 그대로 둔다 |
| 다중성·해석 | 새 검정 없음. 머리말의 굵은 문장(판정점·다시 판정하지 않음)이 그대로 적용된다 |
| 순서·자원 | 다른 등록 runner 가 돌지 않을 때만 시작한다(지금 없음). **CPU 96 스레드**: `taskset -c 24-47,120-143,72-95,168-191 bash code/run_fighsdmi16e4.sh` (사용자 지시 10-12 CDT; runner 는 192 워커를 만들어 96 스레드를 나눠 쓴다 — 결과 불변). 함께 도는 것: ROOM16e4 §7 의 기록 감사(Fable 서브에이전트; CPU 16 스레드 이하, NUMA 노드 0; raw 를 읽기만 한다 — 감사의 반영은 `FIGHS_DONE` 뒤에 커밋한다). **`FIGHS_DONE` (재개가 필요하면 마지막 `--resume` 의 끝)까지 main 커밋을 하지 않고, 작업 트리에서도 `conf/code` · `Demo` · `DECISIONS.md` · 이 문서를 건드리지 않는다**(스크립트의 `# PRE` 줄이 재개 때 다시 본다 — FIGHSX16e4 의 재개가 그렇게 한 번 멈췄다; 검토 S-5). 비용 [추정] FHDMIB16e4 ≈ 65 분(SRB 보강 base 행 39.0 분 × DMI / SRB 주 실행 시간비 46.6 / 28.3), FHSPDMI ≈ 60 분(41.6 분 × 14.9 / 10.4), FHALDDMI ≈ 5 분, 단계 C + 이른 ALD 추정 ≈ 10–15 분 — 합 ≈ 2.5 시간. 메모리: SP 단계 필요 ≈ 264 GB / 가용 ≈ 1040 GB (ROOM16e4 §7.3) |

(§2 라벨·§4 현황 절은 없다 — FIGHSROOM16e4 와 같은 이유.)

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 이 초안 시점 — DMI 의 n = 20480 결과를 보기 전, Sionna 방 두 풀의 보강 결과는 본 뒤)

1. n = 20480 에서 Proposed (V1) 의 실패 수는 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다. 채점: 실패 수 비교(세 부등식이 모두 성립해야 적중).
2. V1 · b\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 "오르는 칸" 이 없다(+3 → +6 dB 칸 포함; 세 곡선 모두 성립해야 적중).
3. +6 dB 와 +9 dB 에서 실패 수 V1 ≤ b\* (점추정; 두 점 모두 성립해야 적중).
4. 두 부분을 따로 채점한다: **4a.** V1 의 +9 dB 실패 수 ≥ 1 / 20480 (곡선이 +9 dB 까지 이어진다). **4b.** V1 의 +15 dB 실패 수 ≤ 5 / 20480.
5. 세 행 모두 대조·수용 통과(`FIGHS_DONE ok=3 fail=0`), 재개 없이 한 번에(시작 줄 1 개).

**메모(예측이 아니다 — 채점하지 않는다)**: n = 2560 에서 V1 의 +6 dB 가 4 건, +9 dB 부터 0 건이었으므로 n = 20480 에서도 V1 의 +12 · +15 dB 가 0 건일 수 있다 — 그러면 곡선은 그 점에서 끊긴 채로 그린다(규칙대로). +12 / +15 dB 를 n = 81920 으로 다시 재는 것(FIGHSX16e4 의 틀)은 **따로 등록해야 하는 다른 실행**이고 사용자가 그림을 보고 정한다; 그 경우에도 이 실행의 n = 20480 점은 기록(집계표 · `F21dmihs_col`)에 남는다. 선례: SRB · SRP 는 n = 20480 그림을 본 뒤 FIGHSX16e4 를 따로 등록했고, 원고판을 +12 dB 까지 그리는 결정(`hsx12`)은 SRB 의 +15 dB 결과를 본 뒤의 사용자 결정이었다(`DECISIONS.md` 10-12).

## 5. 실행 전 기록

v2 2026-10-12 18:43 CDT (Opus 5.5). 검토(MUST 1 · SHOULD 5 · NIT 8) 반영: **M-1** `# EARLY` 줄에 그 행의 두 대조 관문을 넣음(스크립트 196 행; §1 스크립트 칸); S-1 머리말 GMM 항목의 "정상 수렴한" 을 5-DMI 의 캐비엇 문구로; S-2 FIGHSX16e4 의 재개 횟수 정정과 재개 운영 줄; S-3 `DECISIONS.md` 에 "사용자의 별도 지시 없음 — 세션의 해석" 줄(이 커밋), 스크립트 머리말 2–3 행에 "NO separate user instruction for DMI", 그리고 아래 "사용자 확인" 문단; S-4 n = 2560 그림에서 제안 곡선 이하인 baseline 점 12 개를 공개에 적고 §3 의 n = 81920 메모에 "따로 등록" 과 선례를 적음; S-5 마지막 `--resume` 까지 작업 트리도 건드리지 않음; N-1 스크립트 142 행 주석; N-2 이른 호출의 ABORT 줄은 행의 실패가 아님; N-3 "겹친다" 와 기대값; N-4 §3 의 6 번을 번호 밖 메모로, 1 · 2 · 3 번에 "모두 성립해야 적중"; N-5 세션 요약의 따옴표를 뗌; N-6 "같은 파일" 의 근거 문구; N-7 아래 실행 명령과 `HSREG` 커밋; N-8 상속 메모(§1). 검토가 확인한 것: `bash -n`, `sed` 대비 diff, `ROWS` 의 모든 값 = 5-DMI = 디스크(체크포인트·b\* gmm1024 ll_val·`arms.gmm_selection` → gmm1024·pick·ALD 기록·fits), `# PRE` 줄 전부(지금 걸리는 것은 실행 커밋이 해결할 것뿐), `# EARLY` 줄의 재사용 분기·here-string·`ald.py --set hisnr` 의 DMI 경로, `eval_accept` 인자 세 벌(원 raw 에 읽기 전용으로 `ACCEPT: OK`), 그림의 비-hs 기록·PDF 바이트 동일과 `DMI hs` 시험 렌더, 등록의 사실 문장들(값 대조 29 / 29), CPU 배치. 검토가 확인하지 못한 것: GPU 단계와 DMI 의 대조 통과 여부(실행이 본다), 세션 기록 기준 진술. 스크립트 `code/run_fighsdmi16e4.sh` sha256[:16] b32cfd92db26e8e3 = 검토받은 8970b917fed6f67d 에 M-1 (196 행의 관문 두 개) · S-3 (머리말) · N-1 (142 행 주석)만 더한 것(`bash -n` 통과; 다시 검토받지 않았다).

**사용자 확인(검토 S-3)**: 이 보강에 대해 사용자의 확인을 **받지 않았다**. 10-12 CDT 에 baseline 이 끝난 뒤 그림 `F21dmi_col` 을 보내며 "같은 n = 20480 보강을 준비 중" 이라고 알렸고, 이어 상태 보고에서 "DMI 에 대해 따로 지시하신 적은 없고 … 제 판단입니다. 원치 않으시면 말씀해 주세요, 바로 멈춥니다" 라고 적었다; 이 커밋 시점까지 답은 없다. 근거로 삼은 것은 10-11 CDT 의 두 지시(머리말)와 10-12 CDT 의 CPU 상한 지시("192개 중 절반 정도만")뿐이다 — 이 실행은 그 상한(96 스레드) 안에서 돈다. 사용자가 멈추라고 하면 tmux `fighsdmi` 를 끝내고 그때까지의 raw 는 "중단" 으로 기록한다(집계표·그림 없음).

**그림 스크립트**: `HSREG` 에 DMI 항목을 넣은 변경은 커밋 ecaaf967 (이 실행 커밋 앞)에 들어갔다.

**실행 명령(이 커밋 뒤, 한 번)**: `tmux new -d -s fighsdmi -c /home/HTJ/t2/conf "taskset -c 24-47,120-143,72-95,168-191 bash code/run_fighsdmi16e4.sh"`. **실행 커밋 = 이 문서를 담은 커밋**(그 뒤 `FIGHS_DONE` 까지 main 커밋 없음). 실행 시작 전 상태: `raw_FHDMIB16e4` · `raw_FHSPDMI` · `raw_FHALDDMI` · `ald_PILDMI_hisnr.npz` · FHC\*DMI 대조 파일 없음. DMI 의 새 시행 결과는 아무도 보지 않았다. ROOM16e4 §7 의 기록 감사는 이 커밋 시점에 아직 돌고 있다(결과를 보지 않은 채 시작한다; 감사가 §7 의 수치를 고치면 이 문서의 인용(머리말의 n = 2560 실패 수 등)도 §6 에서 밝힌다).

---

## 6. 결과 (기록 2026-10-12 21:37 CDT, Opus 5.5 — 전사만, 해석 없음; 이 절은 추가만 한다)

### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsroom_gen.py`; 수치는 모두 기록 파일에서 읽음)

`bash code/run_fighsdmi16e4.sh` **한 번**, tmux `fighsdmi`, 10-12 18:43 CDT 시작(git e5caaccb = 실행 커밋; 시작 줄 하나, 재개 없음). 단계 C (관측된 시험 청크 0 의 대조) 10-12 18:45 CDT: 3 receiver control(s) OK, 1 ALD estimator control(s) OK. `FIGHS_DONE ok=3 fail=0` 10-12 21:32 CDT. ABORT · SKIP · INVALID 줄: 0 개.

| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |
|---|---|---|---|---|---|---|---|
| FHDMIB16e4 | 10-12 18:49 | 75.3 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-12 20:05 | rc=0; ACCEPT: OK -- FHDMIB16e4; ACCEPT (f): OK | e5caaccb · 66bd25e9fa596040 | CONTROL: OK |
| FHSPDMI | 10-12 20:05 | 82.3 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-12 21:28 | rc=0; ACCEPT: OK -- FHSPDMI; ACCEPT (f): OK | e5caaccb · 66bd25e9fa596040 | CONTROL: OK |
| FHALDDMI | 10-12 21:29 | 2.6 분 · 2048 작업 · 192 워커 | 2048 / 0 | 10-12 21:32 | rc=0; ACCEPT: OK -- FHALDDMI; ACCEPT (f): OK | e5caaccb · 66bd25e9fa596040 | CONTROL: OK · CONTROL-ALD: OK |

수용 파일의 (f) 줄(raw 당 청크 수 · `run|git` · pick · ald · raised):

- `(f) raw_FHDMIB16e4: 2048 chunk files, run|git ['e5caaccb']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FHSPDMI: 2048 chunk files, run|git ['e5caaccb']; pick results/sparse/pick_DMI_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FHALDDMI: 2048 chunk files, run|git ['e5caaccb']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILDMI_hisnr.npz; raised trials per arm (= failures, report only) 0`

집계표 머리말:

- `# run_fighsdmi16e4 git e5caaccb raw_FHDMIB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSDMI16e4 §1); load_raw warnings 0`
- `# run_fighsdmi16e4 git e5caaccb raw_FHSPDMI C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSDMI16e4 §1); load_raw warnings 0`
- `# run_fighsdmi16e4 git e5caaccb raw_FHALDDMI C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSDMI16e4 §1); load_raw warnings 0`

### 6.2 원고 범례 11 곡선 — BLER@16 실패 수 (+6 / +9 / +12 / +15 dB; 새 시행 n = 20480 과 원 raw n = 2560)

| 곡선 (arm) | 출처 | +6 dB: k / 20480 (BLER, 95 % Wilson) | +9 dB: k / 20480 (BLER, 95 % Wilson) | +12 dB: k / 20480 (BLER, 95 % Wilson) | +15 dB: k / 20480 (BLER, 95 % Wilson) | 원 raw k / 2560 (+6 / +9 / +12 / +15) |
|---|---|---|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FHDMIB16e4 | 21 (1.03e-03, [6.71e-04, 1.57e-03]) | 2 (9.77e-05, [2.68e-05, 3.56e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 4 / 0 / 0 / 0 |
| ALD-pilot | raw_FHALDDMI | 58 (2.83e-03, [2.19e-03, 3.66e-03]) | 8 (3.91e-04, [1.98e-04, 7.71e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 4 / 1 / 1 / 0 |
| M-ours-bstar | raw_FHDMIB16e4 | 27 (1.32e-03, [9.06e-04, 1.92e-03]) | 8 (3.91e-04, [1.98e-04, 7.71e-04]) | 2 (9.77e-05, [2.68e-05, 3.56e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 7 / 0 / 0 / 0 |
| R2-ours-G | raw_FHDMIB16e4 | 308 (1.50e-02, [1.35e-02, 1.68e-02]) | 54 (2.64e-03, [2.02e-03, 3.44e-03]) | 6 (2.93e-04, [1.34e-04, 6.39e-04]) | 2 (9.77e-05, [2.68e-05, 3.56e-04]) | 31 / 12 / 0 / 0 |
| R1-turbo | raw_FHDMIB16e4 | 767 (3.75e-02, [3.49e-02, 4.01e-02]) | 153 (7.47e-03, [6.38e-03, 8.75e-03]) | 20 (9.77e-04, [6.32e-04, 1.51e-03]) | 6 (2.93e-04, [1.34e-04, 6.39e-04]) | 90 / 23 / 4 / 0 |
| R3-bigamp | raw_FHDMIB16e4 | 4194 (2.05e-01, [1.99e-01, 2.10e-01]) | 3448 (1.68e-01, [1.63e-01, 1.74e-01]) | 4530 (2.21e-01, [2.16e-01, 2.27e-01]) | 4940 (2.41e-01, [2.35e-01, 2.47e-01]) | 554 / 437 / 573 / 603 |
| R0-pilot@1 | raw_FHDMIB16e4 | 2390 (1.17e-01, [1.12e-01, 1.21e-01]) | 634 (3.10e-02, [2.87e-02, 3.34e-02]) | 145 (7.08e-03, [6.02e-03, 8.32e-03]) | 39 (1.90e-03, [1.39e-03, 2.60e-03]) | 302 / 81 / 23 / 3 |
| SBL-loop | raw_FHSPDMI | 192 (9.37e-03, [8.14e-03, 1.08e-02]) | 20 (9.77e-04, [6.32e-04, 1.51e-03]) | 4 (1.95e-04, [7.60e-05, 5.02e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 16 / 5 / 0 / 0 |
| SBL-pilot | raw_FHSPDMI | 244 (1.19e-02, [1.05e-02, 1.35e-02]) | 41 (2.00e-03, [1.48e-03, 2.71e-03]) | 7 (3.42e-04, [1.66e-04, 7.05e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 20 / 3 / 1 / 0 |
| OMP-pilot | raw_FHSPDMI | 601 (2.93e-02, [2.71e-02, 3.17e-02]) | 114 (5.57e-03, [4.64e-03, 6.68e-03]) | 26 (1.27e-03, [8.67e-04, 1.86e-03]) | 12 (5.86e-04, [3.35e-04, 1.02e-03]) | 80 / 24 / 3 / 0 |
| R5-genie | raw_FHDMIB16e4 | 7 (3.42e-04, [1.66e-04, 7.05e-04]) | 1 (4.88e-05, [8.62e-06, 2.77e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 0 (0.00e+00, [0.00e+00, 1.88e-04]) | 0 / 0 / 0 / 0 |

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FHDMIB16e4 [7, 1, 0, 0] · FHSPDMI [7, 1, 0, 0] · FHALDDMI [7, 1, 0, 0] → 동일.

0 실패 점 (n = 20480): M-ours-dscore-C-V1 +12 dB, M-ours-dscore-C-V1 +15 dB, ALD-pilot +15 dB, M-ours-bstar +15 dB, R5-genie +12 dB, R5-genie +15 dB.

그림 기록 `records/paper_f21dmihs.txt` 의 '오르는 칸' (SNR 이 오를 때 BLER 이 오르는 칸, 한쪽 Fisher p; 보고만): 1 줄.
- `R3-bigamp           @16  4194/20480 3448/20480 4530/20480 4940/20480   (raw_FHDMIB16e4)   rising: +9->+12 dB p=7.4e-42; +12->+15 dB p=8.2e-07`

### 6.3 §3 예측 채점

1. V1 의 실패 수가 +6 ≥ +9 ≥ +12 ≥ +15 dB 로 줄기만 한다 → **적중** (21 / 2 / 0 / 0).
2. V1 · b\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **적중** (오르는 칸의 p: M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음).
3. +6 · +9 dB 에서 실패 수 V1 ≤ b\* → **적중** (21 대 27, 2 대 8).
4a. V1 의 +9 dB 실패 수 ≥ 1 / 20480 → **적중** (2).
4b. V1 의 +15 dB 실패 수 ≤ 5 / 20480 → **적중** (0).
5. `FIGHS_DONE ok=3 fail=0`, 재개 없이 한 번에(시작 줄 1 개) → **적중** (ok=3 fail=0; 시작 줄 1 개).

### 6.4 그림과 공개 사항

- **그림** `conference/figures/F21dmihs_col.{pdf,png}`, 기록 `records/paper_f21dmihs.txt` (§1 의 명령 그대로, `FIGHS_DONE` 뒤; 앞에 `taskset -c 24-39` 만 붙임): 실패 수 = 집계표(스크립트 assert), y 축 (3e-05, 1.2) (기록의 Layout 줄). 0 실패 점 — 기록 원문: `Zero-failure points (the curve breaks there; Perfect CSI: fighs_merge.zero_arrows): Proposed (diffusion prior) +12 dB; Proposed (diffusion prior) +15 dB; Annealed Langevin (plug-in) +15 dB; GMM prior +15 dB; Perfect CSI +12 dB; Perfect CSI +15 dB.` 제안 곡선은 +9 dB 에서 끝나고 +12 · +15 dB 에는 표시가 없다(0 / 20480, Wilson 상한 1.88e-04); Perfect CSI 의 +12 · +15 dB 는 화살표다. Wilson 하한이 y 축 아래(3e-05 미만)라 축에서 잘리는 막대(6.2 의 구간에서 읽음; 막대는 네 곡선에만 있다): Proposed +9 dB (2.68e-05), GMM prior +12 dB (2.68e-05), Gaussian prior +15 dB (2.68e-05), Perfect CSI +9 dB (8.62e-06). −3 / 0 / +3 dB 는 원 raw (n = 2560) 그대로다.
- **'at or below the proposed curve' 줄**(머리말이 옮기기로 한 것; 보강 그림 기록 원문): `Drawn baseline curves (Perfect CSI excluded) at or below the proposed curve (point estimates; failures vs the proposed curve's) -- reported only, nothing is tested here; the registered paired tests are in conf/results/review_next/pairB_SPDMI.txt: Annealed Langevin (plug-in) at +15 dB (0 vs 0); GMM prior at +15 dB (0 vs 0).` n = 2560 그림 기록(`records/paper_f21dmi.txt`)의 같은 줄은 12 점이었다(ROOM16e4 §7.4).
- 새 시행의 ALD 추정 파일 `results/ald/ald_PILDMI_hisnr.npz` sha256[:16] 01d221fb66ceada3 (git 밖). 단계 C 직후 `# EARLY` 줄이 만들었고(운영 로그 10-12 18:45 CDT 줄, GPU 0), 단계 R 이 그대로 썼다(10-12 21:29 CDT 줄 "reusing … (prov git e5caaccb)").
- 실행 중 main 커밋 없음(HEAD e5caaccb 그대로). 작업 트리에서 `conf/code` · `Demo` · `DECISIONS.md` · 이 문서를 건드리지 않았다(`FIGHS_DONE` 뒤 `git status` 로 확인: 바뀐 추적 파일은 `NEXT_EXPERIMENTS_ROOM16e4.md` · `prereg_audit_2026-10-11/s6_fighsroom_gen.py` · `conference/figures/README.md` · `docs/EXPERIMENTS.md` · `docs/RESULTS.md` 와 로그뿐). 함께 돈 것(결과 중립 — 수신기는 CPU 결정적; 세션 기록 기준): ROOM16e4 §7 의 기록 감사(Fable 서브에이전트; CPU, 읽기 전용 — 여섯 청크 재생과 b\* 의 EM 30 반복 연장 포함), 그 감사의 반영 편집(위 다섯 파일 가운데 넷), 작성자의 읽기 전용 조사 `prereg_audit_2026-10-11/gmm_stop_survey.py`, 생성기 `s6_fighsroom_gen.py` 의 DMI 확장(`RUN` 표와 예측 5 의 시작 줄 수)과 `SRP` 회귀 실행.
- **실행 중 작성자가 본 것**: 진행 줄 수와 운영 로그, 그리고 **첫 행의 집계표 `fighs_FHDMIB16e4.txt`** — 그 행의 수용(10-12 20:05 CDT) 뒤 · `FIGHS_DONE` 전에 열어 사용자에게 V1 · b\* · Perfect CSI 의 실패 수를 보고했다(FIGHSPATH16e4 §6.4 의 "`FIGHS_DONE` 뒤에 처음 열었다" 와 다르다). 나머지 두 행의 집계표와 그림은 `FIGHS_DONE` 뒤에 처음 열었다. 그 사이 실행에 손댄 것은 없다(한 번 시작해 스스로 끝남; 세션 기록 기준).
- **사용자 확인**: §5 대로 확인을 받지 않고 시작했고, 시작부터 `FIGHS_DONE` 까지 사용자의 메시지는 없었다(세션 기록 기준).
- §1 의 비용 추정(base ≈ 65 분 · SP ≈ 60 분 · ALD ≈ 5 분, 합 ≈ 2.5 시간) 대비 실측 runner 75.3 · 82.3 · 2.6 분, 전체 10-12 18:43 → 10-12 21:32 CDT (CPU 96 스레드, runner 는 192 워커).
- **머리말의 인용과 ROOM16e4 §7 의 기록 감사**: 감사(MUST 0 · SHOULD 3 · NIT 9; ROOM16e4 §7.8)는 §7 의 수치·라벨을 고치지 않았다 — 머리말이 인용한 n = 2560 실패 수는 그대로다. 감사 S1: b\* 의 EM 은 허용오차 수렴이 아니라 학습 우도가 줄어든 스텝에서 멈췄다(72 반복; 30 반복을 이어 돌리면 ll_val +0.016 nat) — 머리말 GMM 항목의 캐비엇에 더해 읽는다. 이 그림의 GMM prior 곡선은 그 b\* 의 곡선이다.
- +12 · +15 dB 의 n = 81920 측정은 등록하지 않았다 — §3 의 메모대로 사용자가 그림을 보고 정한다.
- 기록 감사(Fable)는 이 절을 쓴 뒤에 받는다 — 결과는 추가 줄로 적는다.
