# NEXT_EXPERIMENTS_FIGHSX16e4 — Sionna RT 방 그림 둘(prior SRB · SRP)의 +12 · +15 dB 점을 새 시행 n = 81920 으로 (범례 11 곡선; **보고 전용**, 등록 v2)

- 작성: 2026-10-11 19:05 CDT, Claude Code (Opus 5.5), 초안 v1 (미커밋; sha256[:16] 96c10efcf72be916) → 적대적 검토 1 건(Fable 5.1 서브에이전트; `prereg_reviews_2026-10-11/review_FIGHSX16e4.md`: 스크립트·`ald.py` 는 그대로 실행 가능, 등록 문서에 MUST 3 · SHOULD 8 · NIT 8 — 반영 내용은 §5) → **v2 2026-10-11 20:39 CDT = 실행 커밋**(§5 를 채운 커밋 = 이 문서를 마지막으로 바꾸는 커밋; `code/run_fighsx16e4.sh` 는 HEAD 가 그 커밋일 때만 돈다). 실행 커밋 뒤 §1 을 바꾸지 않는다.
- 사용자 지시(2026-10-11 CDT, 원문): SRB 의 보강 그림 `F21srbhs_col` 을 보고 **"15dB에서 왜 위로 튀지?"** → 이 세션의 사후 진단(FIGHSROOM16e4 §6.6: Proposed 의 실패가 +12 dB 3 건 → +15 dB 4 건 / 20480, 일곱 블록 모두 조건이 나쁜 채널이고 다른 arm 도 함께 실패, 반복별 실패 수는 줄기만 함)과 두 선택지(① 그대로 둔다 ② +12 · +15 dB 만 시행을 4 배 n = 81920 으로; CPU SRB 약 3 시간 · SRP 약 5 시간; "실제 BLER 이 그 구간에서 평평하면 늘려도 평평하게 나온다" 고 알림) → **"2번 해. 가용 가능한 모든 GPU를 사용해"**.
- **GPU 지시의 처리(공개)**: 수신기 BLER 은 CPU · complex128 로만 잰다 — 01_RULES §9.1 (CPU 기본)과 §9.3 (GPU 경로는 전 arm 같은 정밀도·같은 경로·결정론이 조건이고 §9.4 의 G1 · G2 동등성 검사를 통과해야 한다)에 따라 그렇게 검증된 GPU 수신기 경로는 이 프로젝트에 없고, `runner.py run` 은 `--device cuda` 를 거부한다; 이 틀의 단계 C 대조도 원 raw (CPU)와의 비트 동일을 요구한다. GPU 수신기는 새 측정 도구라 이 등록의 범위 밖이다 → **수신기는 CPU 192 워커 전부, GPU 는 ALD 추정(ALD 행 둘의 대조·새 시행 추정)에만** 쓴다. 사용자에게 그렇게 보고했다(같은 날). GPU 가 Exclusive_Process 라 워커 192 개가 GPU 를 나눠 쓸 수도 없다.
- **틀(새 규칙 없음)** = `NEXT_EXPERIMENTS_FIGHSROOM16e4.md` v2 (SRB) · `NEXT_EXPERIMENTS_FIGHSPATH16e4.md` v2 (SRP) — 둘 다 `NEXT_EXPERIMENTS_FIGHS16e4.md` v2 §1 의 틀 — 에서 **SNR 을 +12 / +15 dB 둘로, 시행을 10000..91919 (n = 81920) 로** 바꾼 것뿐이다. 각 arm 의 체크포인트·적합·조정값·플래그는 ROOM16e4 §5 (SRB) · PATH16e4 §5 (SRP) 의 것 그대로다. 아래에는 그 두 등록과 **다른 곳만** 적는다.
- **보고 전용**: 새 판정 라벨·검정을 등록하지 않는다. 등록된 판정점·라벨·"전부"·"멀어진다" 문장은 ROOM16e4 §6 · PATH16e4 §6 의 것 그대로다. **b\* → V1 의 판정점 −3 / 0 / +3 dB 는 이 보강이 건드리지 않는 SNR 이다. baseline 가운데 R3-bigamp 와 R4-llr 의 판정점은 두 prior 모두 +9 / +12 / +15 dB 라 이 보강의 SNR 을 포함한다(`pairB_SPSRB.txt` · `pairB_SPSRP.txt`); 그 판정·라벨은 원 raw (n = 2560) 로 그대로이고 새 시행으로 다시 판정하지 않는다 — 그림의 +6 dB 이상 점은 그 판정과 다른 시행 집합이며 캡션에 밝힌다.** SRP 의 GMM 캐비엇(b\* 는 EM 이 무너져 선택된 씨앗 초기화; PATH16e4 §5 · 6.1 · 6.7)도 그대로 붙는다.
- **작성 시점 공개**: 작성자와 사용자는 SRB 의 n = 2560 결과와 **n = 20480 결과를 전부 봤다**(FIGHSROOM16e4 §6: +12 / +15 dB 실패 수 / 20480 = V1 3 / 4, ALD-pilot 7 / 11, b\* 11 / 6, R2 37 / 19, R1 87 / 34, BiG-AMP 2813 / 2481, R0@1 376 / 173, SBL-loop 17 / 13, SBL-pilot 23 / 13, OMP 63 / 53, genie 1 / 1) — 그리고 그 +12 · +15 dB 의 시행 20480 개는 **이 실행의 처음 20480 시행과 같은 시행이다**(아래). SRP 의 n = 2560 결과도 전부 봤다; SRP 의 n = 20480 실행(FIGHSPATH16e4)은 이 초안을 쓸 때 도는 중이고 그 결과는 아직 아무도 보지 않았다 — v2 (실행 커밋)는 그 `FIGHS_DONE` 뒤에 만들어지며, 그때 무엇을 봤는지 §5 에 적는다; §3 의 예측은 이 초안의 것이고 v2 에서 바꾸지 않는다. 시행을 늘리는 이유는 "+12 → +15 dB 에서 곡선이 위로 튀어 보인다" 는 것이며, 어느 arm 에 유리한지를 보고 정한 것이 아니다 — 11 곡선 모두 같은 n 으로 다시 잰다. **n = 81920 점은 n = 20480 점과 독립이 아니다**: 처음 20480 시행의 결과를 본 뒤에 늘리기로 했고(계기가 그 시행에서 보인 V1 의 3 → 4 건), 그 시행이 새 점의 4 분의 1 이다. 그래서 n = 81920 의 Wilson 구간은 명목값이며, **보지 않은 시행 30480..91919 (n = 61440) 만의 실패 수·BLER·Wilson 구간을 집계표에 arm · SNR 마다 따로 적는다**(`fighs_FX*.txt` 의 `# split` 줄). 그림의 점은 등록대로 n = 81920 전체이고, 기록·캡션·§6 은 두 수를 나란히 적는다; ALD-pilot 의 "본 시행" 줄은 새 사후 표본이다(아래 '시행').
- **시행**: 새 raw 는 시행 10000..91919 전체(n = 81920)를 **다시 계산한다**. 처음 20480 시행(10000..30479)은 n = 20480 raw (`raw_FH*`)의 +12 · +15 dB 시행과 같은 스트림의 같은 시행(같은 채널·파일럿·잡음)이라, 새 raw 의 처음 512 청크(SNR 마다)는 **ALD-pilot 을 뺀 모든 arm** 에서 그 raw 의 배열을 비트 단위로 재현해야 한다 — 스크립트의 관문은 아니고 **기록 감사가 확인한다**(§3 예측 8). **ALD-pilot 은 예외다**: ALD 추정은 사후 표본이고 `ald.py estimate` 의 씨앗이 파일 안 SNR 순번(`SEED + 1000 + 17k`)과 배치에 묶여 있어 — `hisnr` 파일에서 +12 / +15 dB 는 k = 2 / 3 · 배치 20480, `hisnr4` 에서는 k = 0 / 1 · 배치 81920 — 같은 시행에서도 추정 ĥ 이 다른 표본이다. FXALD 행의 처음 20480 시행의 ALD-pilot 실패 수는 FHALD 의 값(SRB 7 / 11)과 같을 필요가 없다. 시행 30480..91919 는 SRB · SRP 에서 한 번도 쓰인 적이 없다(SRB 의 모든 raw 의 최대 skip 은 `raw_FH*` 의 30440; SRP 는 FIGHSPATH16e4 가 끝나면 같다). 그림의 +12 · +15 dB 점은 **새 raw 하나(n = 81920)** 이다 — n = 20480 raw 의 그 두 점과 합치지 않는다(같은 시행의 부분집합이라 합칠 것도 없다; "한 점 = 한 raw"). **풀 prior 에서 시행 하나는 테스트 풀에서의 복원 추출이다**(SRB 52,353 쌍 · SRP 52,200 스냅숏): 81920 번 추출에서 서로 다른 쌍의 기대 수는 약 4.1 만(풀의 약 79 %)이라, 이 n 에서 점은 "이 풀의 평균 BLER" 에 가까워지는 것이지 새 채널이 늘어나는 것이 아니다; Wilson 구간은 이 풀에 대한 평균 BLER 의 것이다.
- **범위**: 두 prior 의 그림 각 한 장(`F21srbhsx_col` · `F21srphsx_col`). 앞선 그림(`F21sr{b,p}_col` n = 2560, `F21sr{b,p}hs_col` n = 20480)은 그대로 둔다. 원고에 hs · hsx 가운데 어느 것을 쓰는지는 사용자가 정하되, hsx 를 본 뒤 hs 로 돌아가면 그 사실과 두 그림의 +12 · +15 dB 실패 수를 캡션이나 본문에 적는다.

---

## 1. 고정되는 것 (FIGHSROOM16e4 v2 · FIGHSPATH16e4 v2 의 §1 과 다른 곳만)

| 항목 | 값 |
|---|---|
| 행 (`code/run_fighsx16e4.sh` 의 `ROWS`, 이 순서) | **FXSRBB16e4 · FXSPSRB · FXALDSRB** = FIGHSROOM16e4 §1 의 세 행(FHSRBB16e4 · FHSPSRB · FHALDSRB)과 같은 체크포인트(ed437f21af15c305)·b\* (gmm1024, ll_val 97.00871495382869)·pick (4c6da315c701b9d4)·arm·대조 기준; **FXSRPB16e4 · FXSPSRP · FXALDSRP** = FIGHSPATH16e4 §1 의 세 행과 같은 체크포인트(ac4699c78b3e2d80)·b\* (kron 4096, ll_val 244.1932863626755)·pick (6ae22a15de019833)·arm·대조 기준. 다른 것: 태그 접두사 FX, genie 재생 기준 = 같은 prior 의 FX base 행, ALD 행의 `--ald-file /home/HTJ/t2/conf/results/ald/ald_PIL{SRB,SRP}_hisnr4.npz` (새 시행의 ALD 추정: `ald.py regen --set hisnr4` (CPU) + `estimate --set hisnr4` (GPU), 동결된 `tune_PILSRB.json` e0adb06cce792093 · `tune_PILSRP.json` 858087f53952bcbf 그대로). SRB 세 행을 먼저, SRP 세 행을 그 뒤에 |
| 시행·SNR | 새 시행 10000..91919 (`common.HISNR_SKIP0` 부터), **n = 81920**, chunk 40 (행마다 4096 작업), **SNR +12 / +15 dB**; 수신기 CPU, 16 반복; 시행 스트림은 각 prior 의 것(`common.trial_rng`, PID 13 · 15) |
| 스크립트 | `code/run_fighsx16e4.sh` = `code/run_fighsroom16e4.sh` 에서 다음만 바꾼 것(머리말에 원문; 검토가 diff 로 확인 — 행 번호는 검토 때의 것): 머리말 주석, 등록·로그 파일 이름(`logs/run_fighsx16e4.log`), `SNRS="12 15"` · `N=81920`, `ROWS` 표(위 여섯 행), 대조·기준 패턴의 태그 접두사 FH → FX · FHC → FXC, ALD 세트 이름 `hisnr` → `hisnr4` 와 `PILSRP` 의 ALD 기록(테스트 추정 sha ebb14a8952f0ae17, 테스트 파일럿 sha 8bfc83a43f790bbf), 단계 C 요약 줄과 새 실행 전제의 ALD 행 둘, 집계표 머리글과 두 로그 머리글에 찍히는 스크립트·등록 이름, `--resume` 의 읽을 수 없는 청크 검사가 도는 태그 목록(셋 → 여섯), **집계표의 `# split` 줄**(검토 S-1: 시행 10000..30479 = 이미 본 `raw_FH*` 의 시행 / 30480..91919 = 보지 않은 시행; `fighs_merge.parse` 는 `#` 줄을 읽지 않는다), **전제 한 줄**(검토 S-7: `logs/run_fighspath16e4.log` 에 `FIGHS_DONE` 이 있고 살아 있는 `runner.py run` 이 없을 것). 수신기에 넘기는 인자가 다른 곳은 `SNRS` · `N` · `ROWS` · `hisnr4` 뿐이다. 단계 C 대조(테스트 청크 0 = 시행 0..39 에서 +12 · +15 dB 의 원 raw 와 비트 동일; ALD 추정기 대조)가 OK 가 아닌 행은 돌리지 않는다. base 행이 수용되지 않으면 같은 prior 의 SP · ALD 행은 돌리지 않는다(원 스크립트 그대로) |
| 코드 변경 (`conf/code`; 실행 커밋에 포함) | `code/ald.py` 에 세트 `hisnr4` 추가 — 시행 `HISNR_SKIP0`.., n 81920, SNR +12 / +15 dB (세트 정의 두 줄 · `--set` 선택지 · 설명 주석; 추정 경로는 건드리지 않는다). 바뀐 `ald.py` 가 원래 추정을 그대로 내는지는 단계 C 의 ALD 추정기 대조(원 테스트 추정 `ald_PIL*.npz` 와 비트 동일)가 실행 때마다 확인한다. 수신기·runner·`eval_accept` 는 바꾸지 않는다 |
| 수용 | 그 틀 그대로(스크립트): `eval_accept.py --skip0 10000 --n 81920 --points C2:12,15` (청크 계획, meta ntrain / bstar / ll_val, 체크포인트 sha·role, genie 재생), (f) 모든 청크의 `run|git` == HEAD, SP 행 `meta|sparse` == pick, ALD 행 `meta|ald_file`. 통과한 행만 집계표 `results/review_next/fighs_<TAG>.txt` 를 얻는다. 집계표에는 arm · SNR 마다 `# split` 줄이 붙는다(시행 10000..30479 / 30480..91919). 기록 감사가 볼 것(검토 N-7): (f) 줄의 "raised trials per arm" 이 ALD-pilot 에서 0 인지(파일럿 사이트 불일치는 실행을 멈추지 않고 실패로 세어진다), `# split` 의 "seen" 수가 ALD-pilot 을 뺀 모든 arm 에서 `fighs_FH*.txt` 의 수와 같은지 |
| 그림 규칙 | `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21dmc.py <SRB\|SRP> hsx > ~/t2/conference/figures/records/paper_f21<srb\|srp>hsx.txt` → **`F21srbhsx_col` · `F21srphsx_col`**: 곡선마다 −3 / 0 / +3 dB = 원 raw (n = 2560, 등록된 판정의 시행), +6 / +9 dB = `raw_FH<원 태그>` (n = 20480), **+12 / +15 dB = `raw_FX<원 태그>` (n = 81920)** — `fighs_merge.merge` 를 두 번(둘째는 `pre="FX"`, SNR 둘, n 81920; 실패 수는 각 raw 의 집계표와 대조 assert). 나머지는 FIGHSROOM16e4 §1 의 그림 규칙 그대로이되 **y 축에 한 단계를 더한다(검토 M-1; 결과를 보기 전에 정한 규칙)**: `ROOM` 분기 규칙을 그려지는 값에 적용 — (2e-4, 1.2) [0 실패 점이 없고 모든 점·막대 끝이 2e-4 위], 아니면 (3e-5, 1.2) [그려지는 모든 점이 3e-5 이상이고 Perfect CSI 의 0 실패 화살표 끝도 3e-5 이상일 때], 아니면 **(7.5e-6, 1.2)** = FIGHS16e4 의 한계 3e-5 를 n = 20480 → 81920 과 같은 비율로 내린 값(n = 81920 에서 실패 1 건은 1.22e-5 · 2 건은 2.44e-5, 0 실패 화살표는 4.69e-5 에서 2.76e-5 까지 — 3e-5 축에서는 그릴 수 없다); 0 실패 점에서 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표, "오르는 칸" 은 한쪽 Fisher p 와 함께 기록 — **평활화·재실행·점 삭제는 하지 않는다**. 수용되지 않은 FX 행의 곡선은 +12 · +15 dB 에 n = 20480 점을 유지하고 기록·캡션에 밝힌다(`FIGHS_N2560=<FX 태그>`; 기록 줄에 "unchanged, <FX 태그> invalid / unrun" 으로 나온다 — 검토 S-6). 그림 스크립트의 변경은 `hsx` 모드 추가(둘째 merge, y 축의 셋째 단계, 기록 문구), hs 모드 기록 문구 한 곳("counts before the merge …"; FIGHSROOM16e4 감사 N2), `fighs_merge.merge` 의 오류 문구(stderr)와 `FIGHS_N2560` 분기의 FX 문구뿐이고, 비-hs 기록과 hs 그림 파일은 바이트 동일하다(확인; §5) |
| 다중성·해석 | 새 검정 없음. 머리말의 굵은 문장이 그대로 적용된다. 점마다 n 이 다르다(2560 / 20480 / 81920)는 것을 기록·캡션에 적는다 |
| 순서·자원 | FIGHSPATH16e4 가 `FIGHS_DONE` 을 찍은 **뒤**에만 시작한다(CPU 192 워커를 나눠 쓰지 않는다; 그 실행 중에는 main 커밋·`conf/code` 변경 금지). 비용 [추정; 검토 S-4] 단계 C ≈ 10 분; SRB: FXSRBB16e4 ≈ 80 분(FIGHSROOM16e4 의 실측 39.0 분 × 2, 건너뛰는 시행 재생성 +1.7 %), FXSPSRB ≈ 103 분(41.6 분 × 2 × 1.22 — +12 · +15 dB 청크가 278 s 로 네 SNR 평균 228.5 s 보다 길다), FXALDSRB ≈ 13 분(재생성 ≈ 2 분, GPU 추정 ≈ 6–9 분, runner ≈ 4.5 분); SRP: FXSRPB16e4 ≈ 160 분, FXSPSRP ≈ 90 분, FXALDSRP ≈ 13 분 (검토의 추정; FIGHSPATH16e4 의 실측 runner 74.3 · 36.9 · 1.6 분으로 다시 잡으면 base ≈ 151 분 — §5). 합 ≈ 8 시간(7.5–8.5), 밤새 한 번에. 건너뛰는 시행의 재생성은 시행당 0.12 ms (skip 91880 에서 청크당 ≈ 11 s; 검토 실측). 워커 메모리는 n = 20480 실행과 같다. 컨테이너가 다시 만들어져 중단되면 `bash code/run_fighsx16e4.sh --resume` (원 스크립트의 재개 규칙). GPU: 단계 C 의 ALD 추정기 대조 둘(시작 때)과 새 시행 추정 둘(약 3.2 시간째 · 7.7 시간째)에 빈 GPU 한 장씩(스크립트가 고른다) — **밤새 GPU 한 장을 비워 둔다**(GPU 1; 0 · 2 는 등록 밖의 SRB 시드 학습); 빈 GPU 가 없어 ALD 행이 실패하면 `--resume` 은 다른 커밋 전에만 된다. 한 배치 81920 블록의 ALD 추정은 실행 커밋 전에 합성 입력으로 미리 돌려 봤다(§5) |

(§2 라벨·§4 현황 절은 없다 — FIGHSROOM16e4 와 같은 이유.)

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 이 초안 시점 — SRB 의 n = 20480 결과는 본 뒤, SRP 의 n = 20480 결과는 보기 전)

1. SRB, n = 81920: Proposed (V1) 의 실패 수 +15 dB ≤ +12 dB.
2. SRB: V1 · b\* · Perfect CSI 의 곡선에 Fisher p < 0.05 인 "오르는 칸" 이 없다(+9 → +12 → +15 dB 칸; hsx 기록의 rising 줄 — +9 → +12 dB 칸은 n = 20480 대 n = 81920).
3. SRB: +12 dB 와 +15 dB 에서 실패 수 V1 ≤ b\* (점추정; 두 점 따로 채점 — 3a · 3b).
4. SRB: V1 의 n = 81920 실패 수가 +12 dB 에서 5..35, +15 dB 에서 7..41 이다(= k / 81920 이 n = 20480 의 95 % Wilson 구간 [4.98e-05, 4.31e-04] · [7.60e-05, 5.02e-04] 안; 4a · 4b 따로 채점). 이 수에는 이미 본 실패 3 · 4 건이 들어 있다. [검토 S-2: 초안의 반올림 구간 표기를 실패 수로 바꿈 — 내용 같음]
5. SRP, n = 81920: V1 의 실패 수 +15 dB ≤ +12 dB.
6. SRP: +12 dB 와 +15 dB 에서 실패 수 V1 ≤ b\* (6a · 6b).
7. 여섯 행 모두 대조·수용 통과(`FIGHS_DONE ok=6 fail=0`).
8. 새 raw 의 처음 20480 시행(청크 skip 10000..30440)은 +12 · +15 dB 에서 `raw_FH*` 의 같은 이름 청크와 **ALD-pilot 을 뺀 모든 arm × `common.KEYS_RAW`** 배열이 비트 동일하다(여섯 raw 모두 — FXALD 두 raw 에서는 R5-genie 만; 기록 감사가 확인). ALD-pilot 은 씨앗·배치가 달라 대상이 아니다(머리말 '시행'). [검토 M-2 정정: 초안은 "모든 arm" 이라고 적었다 — ALD-pilot 에서는 구조적으로 성립하지 않는다]

예측 1 · 3 · 5 · 6 은 n = 81920 으로 채점하고 n = 61440 (보지 않은 시행)의 수를 옆에 적는다.

## 5. 실행 전 기록

v2 2026-10-11 20:39 CDT (Opus 5.5). **검토(MUST 3 · SHOULD 8 · NIT 8) 반영**: **M-1** y 축 규칙에 셋째 단계 (7.5e-6, 1.2) 를 결과를 보기 전에 등록(§1 그림 규칙; `paper_f21dmc.py` 4 줄 — n = 81920 에서 실패 1 · 2 건인 점과 Perfect CSI 의 0 실패 화살표가 3e-5 축 밖이라 그림 스크립트가 멈추거나 화살표가 사라졌을 것); **M-2** 처음 20480 시행의 비트 동일에서 ALD-pilot 을 예외로(머리말 '시행', 예측 8 — `ald.py estimate` 의 씨앗이 파일 안 SNR 순번·배치에 묶여 있다); **M-3** 스크립트의 "바꾼 것" 목록 보완(§1 · 스크립트 머리말). S-1 n = 81920 점이 n = 20480 점과 독립이 아님을 적고 **보지 않은 61440 시행만의 수를 집계표의 `# split` 줄로 따로 찍음**(스크립트 `counts` 3 줄; 그림 기록 문구); S-2 예측 4 를 실패 수로; S-3 `DECISIONS.md` 줄(이 커밋); S-4 비용 추정을 실측 기준으로; S-5 한 배치 81920 의 ALD 추정을 커밋 전에 시험(아래); S-6 수용되지 않은 FX 행의 기록 문구(`fighs_merge.merge` · `merged()`); S-7 시작 순서 전제 한 줄(스크립트); S-8 GPU 문단의 규칙 인용 정정; N-1 hsx 기록 블록 제목; N-2 `merge` 의 오류 문구도 변경 목록에; N-3 스크립트의 "FHC" 잔재 두 곳; N-5 `zero_arrows` 설명; N-6 hs / hsx 선택 문장; N-7 감사가 볼 항목 둘(§1 수용); N-4 (시험 렌더 전용 문구) · N-8 (상속 메모)은 메모로 남김.

**검토 뒤의 파일**: 스크립트 `code/run_fighsx16e4.sh` sha256[:16] 44fc2e671a63f4be = 검토받은 c942848e55ac9676 에 검토가 준 코드(M-3 머리말 · S-1 `# split` · S-7 전제 · N-3)를 넣은 것(`bash -n` OK); `code/ald.py` f81f3c0f65bed35e = 검토받은 그대로(검토가 STAGED 사본으로 `regen --set hisnr4` 를 실제로 돌려 시행 10000..30479 의 b · H · G · sigma2 가 `pilots_PILSRB_hisnr.npz` 와 비트 동일함을 확인; `ald_py_sha` 를 비교하는 코드는 없음). 그림 코드(`paper_f21dmc.py` · `fighs_merge.py`)는 커밋 aefbfc12 에 들어갔다; 검토 반영 뒤 다시 확인한 것: `SRB` · `SRP` 비-hs 기록과 `SRB hs` 의 기록·PDF·PNG 가 커밋본과 바이트 동일, `FIGHS_ALLOW_MISSING=1 … SRB hsx` 시험 렌더 rc 0, `FIGHS_N2560=<FX 태그> … SRB hsx` 의 기록 줄 "unchanged, FXSRBB16e4 invalid / unrun (FIGHSX16e4 §1)", `fighs_merge.py` 자체 검사 OK (셋째 y 단계 자체는 검토의 합성 계수 하니스가 확인; 이 세션은 다시 돌리지 않았다).

**S-5 GPU 사전 시험** (검토가 만든 `prereg_reviews_2026-10-11/review_FIGHSX16e4_gpu_smoke.py` 를 STAGED `ald.py` 로, GPU 1, 검토 보고(10-11 19:52 CDT) 직후·SRP 실행의 ALD 행(20:30 CDT)보다 먼저; 세션 기록 기준 — 합성 입력(SRB 테스트 파일럿을 81920 행으로 반복), 아무것도 쓰지 않음, 새 시행 미사용): `ald_run B = 81920 on cuda: OK, output (81920, 32), finite True, same seed twice bit-identical True; 0.293 s/step … hisnr4 estimate ~ 8.8 min …; peak GPU memory 8.4 GiB allocated, 10.3 GiB reserved of 95 GiB`.

**이 v2 를 쓰기 전에 본 것(작성 시점 공개의 약속)**: SRP 의 n = 20480 실행(FIGHSPATH16e4)이 끝났고(`FIGHS_DONE ok=3 fail=0`, 10-11 20:36 CDT) 작성자는 그 집계표·그림 `F21srphs_col`·기록을 **전부 봤으며**(FIGHSPATH16e4 §6, 커밋 aefbfc12) 그림은 사용자에게도 보냈다: +12 / +15 dB 실패 수 / 20480 = V1 0 / 0, ALD-pilot 3 / 2, b\* 3 / 1, R2 4 / 1, R1 11 / 4, BiG-AMP 2881 / 2682, R0@1 169 / 55, SBL-loop 8 / 2, SBL-pilot 11 / 2, OMP 30 / 9, genie 1 / 0. §3 의 예측은 그것을 보기 전의 초안 그대로다 — 초안 v1 의 sha256[:16] 96c10efcf72be916 (mtime 10-11 19:05 CDT)은 검토 머리말이 증언하고, 그 시각 SRP 실행은 첫 행을 도는 중이었다(검토의 파일 수 기록: 19:25 CDT 에 1245 / 2048 청크, 집계표 없음). 검토가 바꾼 예측 문구는 4 (실패 수 표기)와 8 (ALD-pilot 예외) 둘이고 [검토 …] 꼬리표를 달았다. **SRP 에서는 V1 이 n = 20480 의 +12 · +15 dB 에서 0 건**이라 이 실행의 SRP 쪽 V1 점은 0–몇 건 수준일 것이다(§1 의 셋째 y 단계가 그 경우를 다룬다). FIGHSPATH16e4 의 실측 runner 시간: 74.3 · 36.9 · 1.6 분(전체 18:34 → 20:36 CDT) → SRP 세 행의 다시 잡은 추정 ≈ 151 · 90 · 13 분.

**운영**: GPU 1 을 비워 둔다(스크립트의 ALD 단계용); GPU 0 · 2 는 등록 밖의 SRB 시드 a2 · a3 학습(10-11 19:26 CDT ~, CPU 스레드 2 개씩 고정), GPU 3 · 4 · 5 는 컨테이너 밖 프로세스가 점유. 실행 뒤 그림은 세션 스크래치의 도우미(`fighsx_figs.sh`: SRB 세 행이 수용되면 §1 의 명령으로 `SRB hsx`, `FIGHS_DONE` 뒤 `SRP hsx`; 로그 `logs/fighsx_figs.log`)가 그린다 — 등록의 일부가 아니고 §1 의 그림 명령을 그대로 부를 뿐이다. **실행 커밋 = 이 문서를 담은 커밋**(그 뒤 `FIGHS_DONE` 까지 main 커밋 없음). 실행 시작 전 상태: `raw_FX*` · `raw_FXC*` · `ald_PIL{SRB,SRP}_hisnr4.npz` · FXC 대조 파일 없음; `logs/run_fighspath16e4.log` 에 `FIGHS_DONE`, 살아 있는 `runner.py run` 없음.

## 6. 결과 (기록 2026-10-12 05:02 CDT, Opus 5.5 — 전사만, 해석 없음; 이 절은 추가만 한다)

### 6.1 실행·운영 기록 (생성기 `prereg_audit_2026-10-11/s6_fighsx_gen.py`; 수치는 모두 기록 파일에서 읽음)

`bash code/run_fighsx16e4.sh`, 실행 커밋 037c6610; 시작 줄 3 개(첫 실행 + `--resume` 2 번), `FIGHS_DONE` 줄 3 개 (`--resume` 호출은 세 번 — 첫 호출은 04:39 CDT 전제 검사에서 시작 줄 없이 중단 [감사 N7]). 운영 로그 `logs/run_fighsx16e4.log` 의 시작 · 단계 C · 종료 · 중단 줄 전부(원문, 시간순):

- `[fighs 10-11 20:40 CDT] start (git 037c6610) rows: all resume=0 skip0 10000 n 81920 SNR 12 15`
- `[fighs 10-11 20:44 CDT] phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK`
- `[fighs 10-12 04:09 CDT] FXALDSRP ABORT: no free GPU for the ALD estimate (resume later; no automatic retry)`
- `[fighs 10-12 04:09 CDT] FIGHS_DONE ok=5 fail=1`
- `[fighs 10-12 04:39 CDT] ABORT (precondition): DECISIONS.md not tracked+clean (commit the registration first)`
- `[fighs 10-12 04:40 CDT] start (git 037c6610) rows: FXALDSRP resume=1 skip0 10000 n 81920 SNR 12 15`
- `[fighs 10-12 04:41 CDT] phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK`
- `[fighs 10-12 04:41 CDT] FXALDSRP SKIP: genie reference FXSRPB16e4 not accepted`
- `[fighs 10-12 04:41 CDT] FIGHS_DONE ok=0 fail=1`
- `[fighs 10-12 04:41 CDT] start (git 037c6610) rows: FXSRPB16e4 FXALDSRP resume=1 skip0 10000 n 81920 SNR 12 15`
- `[fighs 10-12 04:42 CDT] phase C done: 6 receiver control(s) OK, 2 ALD estimator control(s) OK`
- `[fighs 10-12 04:58 CDT] FIGHS_DONE ok=2 fail=0`

| 행 | 시작 (CDT) | runner | 작업 (done / exists) | 수용 (CDT) | 수용 판정 | manifest git · config_hash | 대조 |
|---|---|---|---|---|---|---|---|
| FXSRBB16e4 | 10-11 20:44 | 77.9 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-11 22:02 | rc=0; ACCEPT: OK -- FXSRBB16e4; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXSPSRB | 10-11 22:02 | 100.7 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-11 23:45 | rc=0; ACCEPT: OK -- FXSPSRB; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXALDSRB | 10-11 23:54 | 4.3 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-12 00:00 | rc=0; ACCEPT: OK -- FXALDSRB; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK · CONTROL-ALD: OK |
| FXSRPB16e4 | 10-12 00:00 · 10-12 04:42 | 154.2 · 0.0 분 · 4096 작업 · 192 워커 | 4096 / 4096 | 10-12 02:35 · 10-12 04:42 | rc=0; ACCEPT: OK -- FXSRPB16e4; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXSPSRP | 10-12 02:35 | 92.0 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-12 04:09 | rc=0; ACCEPT: OK -- FXSPSRP; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK |
| FXALDSRP | 10-12 04:52 | 4.5 분 · 4096 작업 · 192 워커 | 4096 / 0 | 10-12 04:58 | rc=0; ACCEPT: OK -- FXALDSRP; ACCEPT (f): OK | 037c6610 · cf706d8f5999293c | CONTROL: OK · CONTROL-ALD: OK |

수용 파일의 (f) 줄:

- `(f) raw_FXSRBB16e4: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXSPSRB: 4096 chunk files, run|git ['037c6610']; pick results/sparse/pick_SRB_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXALDSRB: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr4.npz; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXSRPB16e4: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXSPSRP: 4096 chunk files, run|git ['037c6610']; pick results/sparse/pick_SRP_C2.json; rotation -; ald -; raised trials per arm (= failures, report only) 0`
- `(f) raw_FXALDSRP: 4096 chunk files, run|git ['037c6610']; pick -; rotation -; ald /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr4.npz; raised trials per arm (= failures, report only) 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSRBB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSPSRB C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXALDSRB C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

### 6.2a SRB (방, 무작위 위치) — 범례 11 곡선의 +12 / +15 dB 실패 수: n = 81920 전체, 보지 않은 61440 시행만, 앞선 n = 20480

| 곡선 (arm) | 출처 | +12 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] | +15 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] |
|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FXSRBB16e4 | 12 (1.46e-04, [8.38e-05, 2.56e-04]) · 9 (1.46e-04) · 3 [3] | 11 (1.34e-04, [7.50e-05, 2.40e-04]) · 7 (1.14e-04) · 4 [4] |
| ALD-pilot | raw_FXALDSRB | 40 (4.88e-04, [3.59e-04, 6.65e-04]) · 31 (5.05e-04) · 9 [7] | 31 (3.78e-04, [2.67e-04, 5.37e-04]) · 17 (2.77e-04) · 14 [11] |
| M-ours-bstar | raw_FXSRBB16e4 | 32 (3.91e-04, [2.77e-04, 5.51e-04]) · 21 (3.42e-04) · 11 [11] | 15 (1.83e-04, [1.11e-04, 3.02e-04]) · 9 (1.46e-04) · 6 [6] |
| R2-ours-G | raw_FXSRBB16e4 | 144 (1.76e-03, [1.49e-03, 2.07e-03]) · 107 (1.74e-03) · 37 [37] | 65 (7.93e-04, [6.23e-04, 1.01e-03]) · 46 (7.49e-04) · 19 [19] |
| R1-turbo | raw_FXSRBB16e4 | 319 (3.89e-03, [3.49e-03, 4.34e-03]) · 232 (3.78e-03) · 87 [87] | 127 (1.55e-03, [1.30e-03, 1.84e-03]) · 93 (1.51e-03) · 34 [34] |
| R3-bigamp | raw_FXSRBB16e4 | 11377 (1.39e-01, [1.37e-01, 1.41e-01]) · 8564 (1.39e-01) · 2813 [2813] | 10284 (1.26e-01, [1.23e-01, 1.28e-01]) · 7803 (1.27e-01) · 2481 [2481] |
| R0-pilot@1 | raw_FXSRBB16e4 | 1558 (1.90e-02, [1.81e-02, 2.00e-02]) · 1182 (1.92e-02) · 376 [376] | 676 (8.25e-03, [7.66e-03, 8.89e-03]) · 503 (8.19e-03) · 173 [173] |
| SBL-loop | raw_FXSPSRB | 90 (1.10e-03, [8.94e-04, 1.35e-03]) · 73 (1.19e-03) · 17 [17] | 43 (5.25e-04, [3.90e-04, 7.07e-04]) · 30 (4.88e-04) · 13 [13] |
| SBL-pilot | raw_FXSPSRB | 103 (1.26e-03, [1.04e-03, 1.52e-03]) · 80 (1.30e-03) · 23 [23] | 43 (5.25e-04, [3.90e-04, 7.07e-04]) · 30 (4.88e-04) · 13 [13] |
| OMP-pilot | raw_FXSPSRB | 304 (3.71e-03, [3.32e-03, 4.15e-03]) · 241 (3.92e-03) · 63 [63] | 178 (2.17e-03, [1.88e-03, 2.52e-03]) · 125 (2.03e-03) · 53 [53] |
| R5-genie | raw_FXSRBB16e4 | 5 (6.10e-05, [2.61e-05, 1.43e-04]) · 4 (6.51e-05) · 1 [1] | 4 (4.88e-05, [1.90e-05, 1.26e-04]) · 3 (4.88e-05) · 1 [1] |


**독립이 아님(머리말 '작성 시점 공개') [감사 S1]**: 이 표의 n = 81920 점은 앞선 n = 20480 점과 독립이 아니다 — 처음 20480 시행(10000..30479)은 그 점의 시행 그대로이고(ALD-pilot 만 같은 시행의 새 사후 표본), 그 결과를 본 뒤에 시행을 늘렸다. 그래서 k / 81920 의 Wilson 구간은 명목값이다. 새 증거는 '보지 않은 시행' (30480..91919, n = 61440) 뿐이고 그 Wilson 구간은 집계표의 `# split` 줄에 있다 — SRB: V1 9 · 7 건 [7.71e-05, 2.78e-04] · [5.52e-05, 2.35e-04], b\* 21 · 9 건 [2.24e-04, 5.22e-04] · [7.71e-05, 2.78e-04], Perfect CSI 4 · 3 건 [2.53e-05, 1.67e-04] · [1.66e-05, 1.44e-04].

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FXSRBB16e4 [5, 4] · FXSPSRB [5, 4] · FXALDSRB [5, 4] → 동일. "본 시행" 의 수는 ALD-pilot 을 뺀 모든 arm 에서 n = 20480 raw 의 수와 같다(assert); ALD-pilot 은 새 사후 표본이라 다를 수 있다(등록 머리말 '시행').

0 실패 점 (n = 81920): 없음.

그림 기록 `records/paper_f21srbhsx.txt` 의 '오르는 칸' (한쪽 Fisher p; 보고만): 1 줄. y 축 (3e-05, 1.2).
- `R3-bigamp           @16  2861/20480 2507/20480 11377/81920 10284/81920   (+6..+15 dB: raw_FHSRBB16e4; then +12/+15 dB: raw_FXSRBB16e4)   rising: +9->+12 dB p=2.7e-10`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSRPB16e4 C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXSPSRP C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

집계표 머리말: `# run_fighsx16e4 git 037c6610 raw_FXALDSRP C2: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings 0`

### 6.2b SRP (경로, 이동 단말) — 범례 11 곡선의 +12 / +15 dB 실패 수: n = 81920 전체, 보지 않은 61440 시행만, 앞선 n = 20480

| 곡선 (arm) | 출처 | +12 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] | +15 dB: k / 81920 (BLER, 95 % Wilson) · 보지 않은 시행 k / 61440 (BLER) · 본 시행 k / 20480 [raw_FH 의 k] |
|---|---|---|---|
| M-ours-dscore-C-V1 | raw_FXSRPB16e4 | 4 (4.88e-05, [1.90e-05, 1.26e-04]) · 4 (6.51e-05) · 0 [0] | 1 (1.22e-05, [2.15e-06, 6.91e-05]) · 1 (1.63e-05) · 0 [0] |
| ALD-pilot | raw_FXALDSRP | 11 (1.34e-04, [7.50e-05, 2.40e-04]) · 6 (9.77e-05) · 5 [3] | 4 (4.88e-05, [1.90e-05, 1.26e-04]) · 2 (3.26e-05) · 2 [2] |
| M-ours-bstar | raw_FXSRPB16e4 | 14 (1.71e-04, [1.02e-04, 2.87e-04]) · 11 (1.79e-04) · 3 [3] | 6 (7.32e-05, [3.36e-05, 1.60e-04]) · 5 (8.14e-05) · 1 [1] |
| R2-ours-G | raw_FXSRPB16e4 | 16 (1.95e-04, [1.20e-04, 3.17e-04]) · 12 (1.95e-04) · 4 [4] | 6 (7.32e-05, [3.36e-05, 1.60e-04]) · 5 (8.14e-05) · 1 [1] |
| R1-turbo | raw_FXSRPB16e4 | 44 (5.37e-04, [4.00e-04, 7.21e-04]) · 33 (5.37e-04) · 11 [11] | 11 (1.34e-04, [7.50e-05, 2.40e-04]) · 7 (1.14e-04) · 4 [4] |
| R3-bigamp | raw_FXSRPB16e4 | 11333 (1.38e-01, [1.36e-01, 1.41e-01]) · 8452 (1.38e-01) · 2881 [2881] | 10874 (1.33e-01, [1.30e-01, 1.35e-01]) · 8192 (1.33e-01) · 2682 [2682] |
| R0-pilot@1 | raw_FXSRPB16e4 | 656 (8.01e-03, [7.42e-03, 8.64e-03]) · 487 (7.93e-03) · 169 [169] | 196 (2.39e-03, [2.08e-03, 2.75e-03]) · 141 (2.29e-03) · 55 [55] |
| SBL-loop | raw_FXSPSRP | 14 (1.71e-04, [1.02e-04, 2.87e-04]) · 6 (9.77e-05) · 8 [8] | 8 (9.77e-05, [4.95e-05, 1.93e-04]) · 6 (9.77e-05) · 2 [2] |
| SBL-pilot | raw_FXSPSRP | 20 (2.44e-04, [1.58e-04, 3.77e-04]) · 9 (1.46e-04) · 11 [11] | 8 (9.77e-05, [4.95e-05, 1.93e-04]) · 6 (9.77e-05) · 2 [2] |
| OMP-pilot | raw_FXSPSRP | 124 (1.51e-03, [1.27e-03, 1.80e-03]) · 94 (1.53e-03) · 30 [30] | 38 (4.64e-04, [3.38e-04, 6.37e-04]) · 29 (4.72e-04) · 9 [9] |
| R5-genie | raw_FXSRPB16e4 | 1 (1.22e-05, [2.15e-06, 6.91e-05]) · 0 (0.00e+00) · 1 [1] | 0 (0.00e+00, [0.00e+00, 4.69e-05]) · 0 (0.00e+00) · 0 [0] |


**독립이 아님(머리말 '작성 시점 공개') [감사 S1]**: 이 표의 n = 81920 점도 앞선 n = 20480 점과 독립이 아니다(6.2a 의 같은 문단) — 새 증거는 '보지 않은 시행' 뿐이다: SRP: V1 4 · 1 건 [2.53e-05, 1.67e-04] · [2.87e-06, 9.22e-05], b\* 11 · 5 건 [1.00e-04, 3.21e-04] · [3.48e-05, 1.91e-04], Perfect CSI 0 · 0 건 [0, 6.25e-05] · [0, 6.25e-05].

**GMM 캐비엇(머리말) [감사 S2]**: M-ours-bstar (그림의 GMM prior) 행은 PATH16e4 의 b\* 그대로다 — EM 이 무너져 선택된 씨앗 초기화("kron 4096", ll_val 244.1933, it_best 0)이고 잘 맞춘 GMM 이 아니다. n = 81920 의 실패 수는 b\* 14 / 6 (보지 않은 시행 11 / 5), Gaussian prior (R2-ours-G) 16 / 6 (보지 않은 시행 12 / 5).

Perfect CSI (R5-genie) 의 실패 수는 세 raw 에서 같다: FXSRPB16e4 [1, 0] · FXSPSRP [1, 0] · FXALDSRP [1, 0] → 동일. "본 시행" 의 수는 ALD-pilot 을 뺀 모든 arm 에서 n = 20480 raw 의 수와 같다(assert); ALD-pilot 은 새 사후 표본이라 다를 수 있다(등록 머리말 '시행').

0 실패 점 (n = 81920): R5-genie +15 dB.

그림 기록 `records/paper_f21srphsx.txt` 의 '오르는 칸' (한쪽 Fisher p; 보고만): 1 줄. y 축 (7.5e-06, 1.2).
- `R3-bigamp           @16  3386/20480 2585/20480 11333/81920 10874/81920   (+6..+15 dB: raw_FHSRPB16e4; then +12/+15 dB: raw_FXSRPB16e4)   rising: +9->+12 dB p=2.7e-06`

### 6.3 §3 예측 채점 (n = 81920 으로 채점; 괄호 안의 둘째 수는 보지 않은 61440 시행만의 수)

1. SRB: V1 의 실패 수 +15 dB ≤ +12 dB → **적중** (12 → 11; 보지 않은 시행 9 → 7).
2. SRB: V1 · b\* · Perfect CSI 에 Fisher p < 0.05 인 오르는 칸 없음 → **적중** (오르는 칸의 p: M-ours-dscore-C-V1 없음, M-ours-bstar 없음, R5-genie 없음).
3a. SRB: +12 dB 에서 실패 수 V1 ≤ b\* → **적중** (12 대 32; 보지 않은 시행 9 대 21).
3b. SRB: +15 dB 에서 실패 수 V1 ≤ b\* → **적중** (11 대 15; 보지 않은 시행 7 대 9).
4a. SRB: V1 의 +12 dB 실패 수가 5..35 → **적중** (12).
4b. SRB: V1 의 +15 dB 실패 수가 7..41 → **적중** (11).
5. SRP: V1 의 실패 수 +15 dB ≤ +12 dB → **적중** (4 → 1; 보지 않은 시행 4 → 1).
6a. SRP: +12 dB 에서 실패 수 V1 ≤ b\* → **적중** (4 대 14; 보지 않은 시행 4 대 11; b\* 는 씨앗 초기화 GMM — 머리말 캐비엇 [감사 S2]).
6b. SRP: +15 dB 에서 실패 수 V1 ≤ b\* → **적중** (1 대 6; 보지 않은 시행 1 대 5; b\* 는 씨앗 초기화 GMM — 머리말 캐비엇 [감사 S2]).
7. 여섯 행 모두 대조·수용 통과(`FIGHS_DONE ok=6 fail=0`) → **빗나감** (첫 실행의 종료 줄 ok=5 fail=1; 시작 줄 3 개; 재개까지 마친 뒤 수용 파일이 `ACCEPT: OK` 인 행 6 / 6 — 엄격 채점: 한 번의 실행으로 ok=6 이 아니면 빗나감).
8. 처음 20480 시행이 `raw_FH*` 와 비트 동일(ALD-pilot 제외) → **적중** (작성자의 확인 `prereg_audit_2026-10-11/fx_overlap_check.py`; 기록 감사가 따로 확인한다):
   - `raw_FXSRBB16e4 vs raw_FHSRBB16e4: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['M-ours-bstar', 'M-ours-dscore-C-V1', 'R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'R5-genie'], 67584 array comparisons, 0 differ`
   - `raw_FXSPSRB vs raw_FHSPSRB: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['OMP-pilot', 'R5-genie', 'SBL-loop', 'SBL-pilot'], 37888 array comparisons, 0 differ`
   - `raw_FXALDSRB vs raw_FHALDSRB: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['R5-genie'], 13312 array comparisons, 0 differ; ALD-pilot (not required): 3214 of 9216 arrays differ`
   - `raw_FXSRPB16e4 vs raw_FHSRPB16e4: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['M-ours-bstar', 'M-ours-dscore-C-V1', 'R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'R5-genie'], 67584 array comparisons, 0 differ`
   - `raw_FXSPSRP vs raw_FHSPSRP: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['OMP-pilot', 'R5-genie', 'SBL-loop', 'SBL-pilot'], 37888 array comparisons, 0 differ`
   - `raw_FXALDSRP vs raw_FHALDSRP: 1024 chunk files (expected 1024 = 512 x 2 SNR), arms ['R5-genie'], 13312 array comparisons, 0 differ; ALD-pilot (not required): 3229 of 9216 arrays differ`
   - `OVERLAP: OK`

### 6.4 그림과 공개 사항

- **그림 (§1 의 명령 그대로)**: `conference/figures/F21srbhsx_col.{pdf,png}` + 기록 `records/paper_f21srbhsx.txt` (10-12 00:03 CDT — SRB 세 행이 수용된 직후, SRP 행들이 도는 동안 스크래치 도우미 `fighsx_figs.sh` 가 그림; y 축 (3e-05, 1.2), 0 실패 점 없음), `F21srphsx_col.{pdf,png}` + `records/paper_f21srphsx.txt` (10-12 04:59 CDT — 재개가 끝난 뒤 §1 의 명령을 직접 실행; 도우미는 04:10 CDT 에 'SRP rows not all accepted -- no SRP figure' 로 끝났다(`logs/fighsx_figs.log`) [감사 N5]; **y 축 (7.5e-06, 1.2) = §1 의 셋째 단계**: V1 의 +15 dB 점이 1 / 81920 = 1.22e-05 이고 Perfect CSI 의 +15 dB 가 0 / 81920 이라 화살표 끝이 3e-5 아래; 0 실패 점은 Perfect CSI +15 dB 하나). 두 그림 모두 −3 / 0 / +3 dB 는 원 raw (n = 2560), +6 / +9 dB 는 `raw_FH*` (n = 20480), +12 / +15 dB 는 `raw_FX*` (n = 81920). SRP 그림의 GMM prior 곡선은 PATH16e4 의 씨앗 초기화 b\* 의 곡선이다(머리말 캐비엇). **[감사 N1]** SRB 의 y 축 (3e-05, 1.2): 0 실패 점은 없지만 2e-4 이하의 막대 끝이 여섯(Proposed +12 · +15 dB 의 Wilson 하한 8.38e-05 · 7.50e-05, GMM prior +15 dB 1.11e-04, Perfect CSI +9 · +12 · +15 dB 1.04e-04 · 2.61e-05 · 1.90e-05)이라 둘째 범위이고, 가장 낮은 점 4 / 81920 = 4.88e-05 가 3e-5 이상이라 셋째 단계는 아니다; Perfect CSI +12 · +15 dB 의 막대 아래 끝(2.61e-05 · 1.90e-05)은 축 아래로 잘린다. SRP 의 셋째 단계를 만드는 값은 셋이다: Proposed +15 dB 1 / 81920 = 1.22e-05, Perfect CSI +12 dB 1 / 81920 = 1.22e-05, Perfect CSI +15 dB 화살표 끝 2.76e-05; Proposed +15 dB 와 Perfect CSI +12 dB 의 막대 아래 끝(2.15e-06)은 7.5e-6 아래로 잘린다. 원고판의 y 축(같은 규칙을 그려지는 점에만): SRB (3e-05, 1.2), SRP (7.5e-06, 1.2) — SRP 는 Perfect CSI +12 dB 점 하나가 정한다.
- **원고판 (+12 dB 까지; 등록 밖의 제시 선택 — 사용자 결정, `DECISIONS.md` 10-12 14:34 KST 줄)**: `F21srbhsx12_col` · `F21srphsx12_col` (+ 기록 `records/paper_f21sr{b,p}hsx12.txt`; 그림 모드 `paper_f21dmc.py <PRIOR> hsx12`). 사용자는 SRB 의 n = 81920 결과(Proposed +12 / +15 dB = 12 / 11 건, GMM 32 / 15 건)와 전 구간 그림을 본 뒤 "12dB 까지만 paper에 포함시키는 방안도 고려해봐야겠어" · "우리에게 유리하지 않은 것을 굳이 넣을 필요는 없어." 라고 정했다. +15 dB 의 수는 이 절의 표·집계표·전 구간 그림에 그대로 있다. **[감사 S3]** 이 결정은 SRB 의 +15 dB 결과만 본 시점(10-12 00:34 CDT)의 것이다 — SRP 의 n = 81920 행은 그 뒤(02:35 · 04:09 · 04:58 CDT)에 수용됐고, `F21srphsx12_col` 은 같은 모드로 만들어 두었을 뿐 **SRP 원고판의 범위는 사용자 확인 대기**다(`DECISIONS.md` 10-12 19:03 KST 줄). 원고판에 그려지지 않는 +15 dB 점(실패 수 / 81920; 괄호는 보지 않은 61440 시행만): SRB Proposed 11 (7) · GMM 15 (9) · Perfect CSI 4 (3), SRP Proposed 1 (1) · GMM 6 (5) · Perfect CSI 0 (0); 같은 그림의 +12 dB 는 SRB 12 · 32 · 5, SRP 4 · 14 · 1. 등록된 판정점이 +9 / +12 / +15 dB 인 BiG-AMP 의 +15 dB 점도 원고판에는 없다. 감사는 머리말 '범위' 의 규칙과 같은 취지로 "원고판을 쓰면 캡션이나 본문에 +15 dB 도 측정했고 그리지 않았다는 사실과 그 실패 수를 적을 것" 을 권했다 — 캡션·본문은 사용자가 정한다; 작성자는 결정 전에 같은 권고(캡션에 한 문장)를 한 번 전했고 사용자의 답은 위 인용 그대로다. 이 등록은 그 의무를 정하지 않았다.
- **첫 실행에서 FXALDSRP 가 돌지 못했다 — GPU 없음**: 10-12 04:09 CDT 에 `no free GPU for the ALD estimate`; `FIGHS_DONE ok=5 fail=1`. 그 시각 GPU 여섯 장이 모두 컨테이너 밖 프로세스에 점유돼 있었다(이 컨테이너의 프로세스 없음 — `nvidia-smi --query-compute-apps` 가 빈 출력; 비워 둔 GPU 1 은 10-12 00:39 CDT 확인 때부터 밖의 프로세스가 635 MiB 를 쓰고 있었고, GPU 0 · 2 는 등록 밖의 SRB 시드 학습이 00:55 · 01:33 CDT 에 끝난 뒤 밖의 프로세스가 가져갔다). 점유된 GPU 에는 접근하지 않았다.
- **재개 세 번 (같은 HEAD 037c6610; 원인을 하나씩 고침)**: ① 04:39 CDT — GPU 1 이 비자 스크래치 감시 스크립트(`fx_resume_when_free.sh`, 로그 `logs/fx_resume_watch.log`; `nvidia-smi` 만 보고 한 번만 시작)가 `--resume FXALDSRP` 를 시작 → 전제 검사에서 중단: `DECISIONS.md` 에 작성자가 실행 중에 써 둔 미커밋 줄 둘(FIGHSPATH16e4 감사 정정 줄, +12 dB 결정 줄)이 있었다. 작성자가 그 작업본을 스크래치로 옮기고 `git checkout -- DECISIONS.md` 로 커밋 상태로 되돌렸다(재개가 끝난 뒤 다시 넣음). ② 04:40 CDT `--resume FXALDSRP` → `SKIP: genie reference FXSRPB16e4 not accepted`: 행을 하나만 지정하면 기준 행의 수용 표시(`ACC`)가 그 실행에 없어서다(스크립트의 동작; 작성자의 지정 실수). ③ 04:41 CDT `--resume FXSRPB16e4 FXALDSRP` → 기준 행은 4096 청크가 모두 `exists` (새 계산 없음; 수용·집계표를 다시 만들었고 집계표의 수는 같다), FXALDSRP 는 재생성(CPU) + 추정(GPU 1, 04:43 → 04:52 CDT) + runner 4.5 분 → 04:58 CDT `ACCEPT: OK`, `FIGHS_DONE ok=2 fail=0`. **[감사 S4]** 재개는 선택한 행의 단계 C 도 다시 돌렸다: ② 는 FXALDSRP 의 ALD 추정기 대조(GPU 1, 04:40 CDT)와 수신기 대조(청크 2 개 `exists`), ③ 은 그 둘을 한 번 더(GPU 1, 04:41 CDT)와 FXSRPB16e4 의 수신기 대조(`exists`). 재개가 덮어쓴 파일: `fighs_FXSRPB16e4.txt` · `FXSRPB16e4_accept.txt` · `run_manifest_FXSRPB16e4.json` (`written` 이 2026-10-12 18:42:43 KST 로 바뀜 — 첫 실행의 manifest 는 남아 있지 않다) · `FXCSRPB16e4_control.txt` · `FXCALDSRP_control.txt` · `FXCALDSRP_aldcontrol.txt` · `results/ald/ald_FXCALDSRP.npz`. raw 청크는 하나도 다시 쓰이지 않았다(`raw_FXSRPB16e4` 의 mtime 00:06–02:34 CDT, 대조 raw 20:41–20:44 CDT). 감사가 바뀌지 않은 raw 에서 다시 만든 집계표·대조 파일이 지금 파일과 바이트 동일하고, manifest 요약 줄은 두 실행의 로그에서 같다. 여섯 raw 의 모든 청크가 `run|git` 037c6610 이고 실행 내내 main 커밋은 없었다. §3 예측 7 은 빗나감으로 채점했다(한 번의 실행으로 ok=6 이 아니었다).
- **실행 중에 본 것**: 작성자는 10-11 22:35 CDT 에(SRB 의 SP 행이 도는 동안) 수용된 `fighs_FXSRBB16e4.txt` 를 읽어 V1 · b\* · genie 의 수를 사용자에게 보고했고, 00:03 CDT 의 SRB 그림을 사용자에게 보냈다 — 그 뒤 사용자가 위의 +12 dB 결정을 했다(SRP 의 n = 81920 결과가 나오기 전). SRP 행들의 집계표는 첫 `FIGHS_DONE` (04:09 CDT) 뒤에 읽었고, FXALDSRP 가 없는 임시 그림 둘(`FIGHS_N2560=FXALDSRP` — ALD 곡선만 +12 · +15 dB 에 n = 20480 유지; 스크래치에만 둠)을 재개 전에 사용자에게 보냈다. 최종 그림은 재개 뒤의 것이다.
- **실행 중 작업 트리의 변경(커밋은 이 §6 과 함께)**: 그림 스크립트 `paper_f21dmc.py` 에 `hsx12` 모드(10-12 00:32 CDT — SRB 의 hsx 그림 00:03 뒤, SRP 의 hsx 그림 04:59 전; 바뀐 스크립트로 `SRB hsx` 를 다시 돌린 기록·PDF·PNG 가 00:03 의 것과 바이트 동일함을 확인), FIGHSPATH16e4 의 감사 반영(다른 문서들), 진단 스크립트의 시행 번호 표기. `conf/code` · `Demo` 는 실행 커밋 그대로다.
- 함께 돈 것(결과 중립 — 수신기는 CPU 결정적; 세션 기록 기준): SRB 시드 a2 · a3 학습(GPU 0 · 2, 10-11 19:26 → 10-12 00:55 · 01:33 CDT), FIGHSPATH16e4 의 기록 감사(Fable 서브에이전트, CPU 3 스레드 이하), SRB 의 사후 진단 파일 재생성, 그림 렌더, `fx_overlap_check.py` (SRB 세 raw 는 SRP 행들이 도는 동안, 전체는 재개 뒤 — `FX_overlap_check.txt`).
- 새 시행의 ALD 추정 파일(git 밖): `ald_PILSRB_hisnr4.npz` sha256[:16] dcdce65b032899b1, `ald_PILSRP_hisnr4.npz` 2608bcf1c02fe80c.
- §1 의 비용 추정(단계 C ≈ 10 분; 80 · 103 · 13 분; SRP 160 · 90 · 13 분; 합 ≈ 8 시간) 대비 실측 runner 77.9 · 100.7 · 4.3 분, 154.2 · 92.0 · 4.5 분; 첫 실행 10-11 20:40 → 10-12 04:09 CDT (7 시간 29 분), 재개까지 04:58 CDT.
- 기록 감사(Fable)는 이 절을 쓴 뒤에 받는다 — 결과는 추가 줄로 적는다(예측 8 의 독립 확인 포함).

### 6.5 기록 감사 (Fable 5.1 서브에이전트, 보고서 파일 mtime 2026-10-12 05:33 CDT; `prereg_audit_2026-10-11/audit_FIGHSX16e4.md`, 재계산 `recompute_fighsx.py` → `.out`, 등록 도구 재실행 `rerun_fighsx_accept_FX*.txt` · `rerun_fighsx_s6gen.md`)

감사 대상 = 커밋 4c536f1b. **§6.1–6.4 의 수치·채점·인용 오류 0**: 자체 판독기로 새 raw 여섯(24,576 청크; 모든 청크 `run|git` 037c6610, `+dirty` 없음 — 재개 때 쓰인 `raw_FXALDSRP` 포함; raised 블록 없음)·`raw_FH*` (12,288 청크)·원 raw 를 직접 읽음 — 기록 값 약 3,400 개, 배열 비교 356,722 건, 검사 묶음 98 개 중 96 통과(나머지 둘은 아래 M1). 등록의 diff 는 §6 만 건드림; 집계표 여섯(`# split` 56 줄 포함)이 raw 에서 다시 만든 것과 바이트 동일; "본 시행" 의 수는 ALD-pilot 을 뺀 모든 칸에서 `fighs_FH*.txt` 와 같음; `eval_accept` 여섯 행 재실행 → `ACCEPT: OK`; 생성기 재실행이 6.1–6.3 과 바이트 동일; 그림 8 개 모드(`hsx` · `hsx12` · `hs` · 기본 × SRB · SRP) 재렌더가 커밋본과 바이트 동일(기록 8 · PDF/PNG 16); y 축 두 범위가 감사의 자체 구현과 일치; 재개 때 `raw_FXSRPB16e4` 는 다시 쓰이지 않음(청크 mtime 00:06–02:34 CDT); 037c6610 과 4c536f1b 사이에 커밋 없음; 예측 7 의 빗나감 채점이 맞음.

**[감사: 예측 8 의 독립 확인]** 자체 코드로 여섯 raw 의 skip 10000..30440 청크 1024 개씩을 `raw_FH*` 의 같은 이름 청크와 비교: ALD-pilot 을 뺀 모든 arm 의 배열 62464 / 32768 / 8192 / 62464 / 32768 / 8192 개가 바이트 동일(다른 것 0), `run|skip·snr·n·seed·iters` 5120 개씩 동일(`FX_overlap_check.txt` 의 'array comparisons' 67584 / 37888 / 13312 는 이 둘의 합 [감사 N4]). ALD-pilot: SRB 9216 중 3214 개 배열이 다름(nmse 1024 · tauL_gmean 1024 · alphaD 846 · alphaD_clip 143 · ber 113 · blk_err 64), SRP 3229 개(1024 · 1024 · 907 · 227 · 27 · 20); 그 20480 시행의 실패 수 +12 / +15 dB 는 SRB 새 raw 9 / 14 대 `raw_FHALDSRB` 7 / 11 (두 raw 에서 모두 실패한 블록 7 / 10), SRP 5 / 2 대 3 / 2 (모두 실패 3 / 2). `ald_PIL*_hisnr4.npz` 의 처음 20480 행은 파일럿 관측 b 가 `hisnr` 파일의 +12 / +15 dB 행과 비트 동일하고 ĥ 은 20480 행 모두 다르다(`ald.py` 의 씨앗이 파일 안 SNR 순번에 묶여 있음을 코드에서 확인; `aefbfc12..037c6610` 의 `ald.py` diff 는 `hisnr4` 세트뿐).

**MUST 1 · SHOULD 4 · NIT 7 — 모두 반영(이 절의 수치·채점 불변; 기록 2026-10-12 05:35 CDT, Opus 5.5)**: **M1** (다른 문서) `docs/EXPERIMENTS.md` 의 이 실험 행 · `DECISIONS.md` 19:03 KST 줄 · `WORK_QUEUE.md` 의 "예측 12 개 중 11 적중" 은 틀린 셈이었다 — 채점 항목은 **11 개**(1 · 2 · 3a · 3b · 4a · 4b · 5 · 6a · 6b · 7 · 8)이고 **10 개 적중**, 7 번 빗나감; 세 곳을 고치고 `DECISIONS.md` 에 정정 줄(작성자는 사용자에게도 "12개 중 11개" 라고 보고했다 — 정정해 알린다). S1 "독립이 아님" 문단을 6.2a · 6.2b 의 표 뒤에; S2 SRP 의 GMM 캐비엇을 6.2b 와 6.3 의 6a · 6b 에; S3 원고판 결정의 시점(SRB 결과만 본 때)·SRP 판은 확인 대기·그려지지 않는 +15 dB 의 수·감사의 캡션 권고와 그 상태(6.4); S4 재개가 다시 돌린 단계 C 와 덮어쓴 파일 목록(6.4). N1 y 축 범위의 이유 전부(6.4); N2 원고판 기록 문구에 "SRB 의 +15 dB 결과를 본 뒤" 를 넣고 SRP 의 hs · hsx · hsx12 기록에 GMM 캐비엇 한 줄(`paper_f21dmc.py`; 그림 파일은 바이트 동일 — 기록 네 개를 다시 만듦), `docs/EXPERIMENTS.md` 행의 원고판 문구; N3 같은 행의 GPU 시각에 04:41 CDT 추가; N4 비교 건수의 구성(위); N5 SRP 그림을 누가 그렸는지(6.4); N6 (다른 문서) FIGHSPATH16e4 §6.5 의 "확인하지 못한 것" 에 두 항목 추가; N7 시작 줄 수와 `--resume` 호출 수(6.1). 감사가 확인하지 못한 것: 세션 기록 기준 진술(04:09 · 00:39 CDT 의 GPU 점유, 사용자에게 보낸 것과 그 시각, `git checkout -- DECISIONS.md`, 사용자 인용), 재개가 덮어쓴 파일의 첫 실행판(남아 있지 않음), GPU 위의 재실행, `highsnr_fail_SRB.py` 기본 모드의 재실행, 머리말의 풀 통계.
