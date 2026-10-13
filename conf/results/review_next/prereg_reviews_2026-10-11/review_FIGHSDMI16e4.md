# 적대적 사전 검토 — NEXT_EXPERIMENTS_FIGHSDMI16e4.md 초안 v1 (미커밋; sha256[:16] f45e7127c24913b3, mtime 2026-10-12 18:25:36 CDT) + `code/run_fighsdmi16e4.sh` (미추적; sha256[:16] 8970b917fed6f67d, mtime 2026-10-12 18:23:16 CDT) + `conference/figures/paper_f21dmc.py` 의 `HSREG` 한 줄 (sha256[:16] e97bf3565b14c23e)

검토자: Claude Fable 5.1 서브에이전트, 2026-10-12 18:39 CDT 종료. 읽기 전용(`bash -n`, `diff`, sha256sum, 읽기 전용 git, npz 머리 읽기, `eval_accept.py` 를 원 raw 에 읽기 전용으로, 그림 스크립트를 `FIG_OUTDIR=<세션 스크래치>` 로 4 번; CPU 16 스레드 이하(`taskset -c 48-63`), `python -B`, GPU 미사용 — `nvidia-smi` 조회만). 검토 시작 때 HEAD cde35a4e, 검토 중 28fde5dd (18:27 CDT) · ecaaf967 (18:28 CDT) 가 올라갔다 — ecaaf967 이 `HSREG` 변경을 담았고 `conf/code` · `Demo` · `DECISIONS.md` 는 세 커밋에서 그대로다. 검토 끝에 초안·스크립트의 sha 를 다시 읽었다(위와 같음). 틀이 같은 부분은 `review_FIGHSPATH16e4.md` · `review_FIGHSROOM16e4.md` 의 확인을 다시 유도하지 않았다.

## 판정

**수정 후 실행 가능** — MUST 1 · SHOULD 5 · NIT 8.

명목 경로(대조 OK, 빈 GPU 있음)에서는 지금 스크립트로도 세 행이 돌고 수용·집계·그림까지 간다: `ROWS` 의 모든 값이 5-DMI 와 디스크에 맞고, `# PRE` 줄 가운데 지금 실패하는 것은 실행 커밋이 해결할 셋뿐이며, `eval_accept` 인자 세 벌은 원 raw 에서 통과한다. MUST 는 새로 넣은 `# EARLY` 줄이 대조 판정을 보지 않는다는 것(실패 경로에서 §1 의 문장이 거짓이 되고, 대조를 거치지 않은 추정이 재개 때 재사용될 수 있다)이다. 한 줄 수정이다.

## MUST

### M-1 `# EARLY` 줄이 대조 판정을 보지 않는다 (스크립트 195 행; §1 "스크립트" 칸의 "단계 C 대조가 OK 가 아닌 행은 돌리지 않는다")
- 부모 스크립트에서 `ald_new` 는 단계 R 본문 안, 세 관문(201 행 `CONTROL: OK`, 202 행 `CONTROL-ALD: OK`, 203 행 genie 기준 행 수용) **뒤** 204 행에서만 불렸다. 195 행은 그 관문 없이 부른다.
- 결과: (1) ALD 추정기 대조가 FAILED 이거나 빈 GPU 가 없어 판정 파일이 비어 있어도, 수신기 대조가 도는 몇 분 사이에 GPU 가 비면 새 시행 81,920 블록의 `pilots_PILDMI_hisnr.npz` · `ald_PILDMI_hisnr.npz` 를 만든다 — 돌리지 않기로 한 행의 첫 두 단계다. (2) 그 뒤 `--resume` 은 그 파일을 `prov git == HEAD` 만 보고 재사용한다(141–145 행) — 추정기 대조가 OK 가 아니던 호출에서 만든 추정이 ALD 곡선에 들어갈 수 있다. 부모 스크립트에서는 추정이 언제나 같은 호출의 OK 대조 뒤에 만들어졌다.
- 명목 경로에는 영향이 없다(대조 OK → 같은 추정).
- 고칠 것 — 195 행을 다음으로(스크래치 사본에서 `bash -n` 통과; `grep <파일>` 은 here-string 을 읽지 않는다):
  ```
  while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do sel $TAG || continue; [[ $FL == *--ald-file* ]] && grep -qx 'CONTROL: OK' $OUT/${TAG/FH/FHC}_control.txt 2>/dev/null && grep -qx 'CONTROL-ALD: OK' $OUT/${TAG/FH/FHC}_aldcontrol.txt 2>/dev/null && { ald_new || log "$TAG early ALD estimate not made (phase R tries once more)"; }; done <<< "$ROWS"  # EARLY
  ```
  §1 "스크립트" 칸의 `# EARLY` 설명에 덧붙일 문장: "이 줄은 그 행의 수신기 대조와 ALD 추정기 대조가 둘 다 OK 일 때만 추정을 만든다(단계 R 의 201 · 202 행과 같은 검사). genie 기준 행(FHDMIB16e4)의 수용은 아직 없으므로 보지 않는다 — 기준 행이 수용되지 않으면 ALD 행은 SKIP 되고 추정 파일만 남는다(그 뒤의 `--resume FHDMIB16e4 FHALDDMI` 가 재사용)." 스크립트 sha 를 §1 · §5 에서 갱신한다(행 번호 2–10 · 20–22 · 171 · 195 는 그대로다).

## SHOULD

### S-1 머리말 "GMM" 항목의 "정상 수렴한" 은 5-DMI 의 등록된 캐비엇과 어긋난다
- 5-DMI "최종 b\*" 칸: "격자 끝 캐비엇 … **수렴 캐비엇(재시드 6,847)**". 적합 파일: `n_iter` 72 / `it_best` 70, `n_reseed` 6847. 초안은 "정상 수렴한 full 공분산 K = 1024 (…; 격자 끝 캐비엇 …)" 로 수렴 캐비엇을 빼고 반대 말을 붙였다.
- 바꿀 문장: "DMI 의 b\* 는 full 공분산 K = 1024 다(ll_val 112.04253042212595; EM 이 초기화에서 멈춘 SRP 와 달리 it_best 70 / n_iter 72 에서 선택됐다; **격자 끝 캐비엇 + 수렴 캐비엇(재시드 6,847)** — ROOM16e4 5-DMI · §7.1). 보강은 그 b\* 를 그대로 쓴다(다시 맞추지 않는다)."

### S-2 §1 "스크립트": "FIGHSX16e4 는 마지막 행에서 'no free GPU' 로 한 번 재개했다" 는 기록과 다르다
- `logs/run_fighsx16e4.log`: 31 행 `FXALDSRP ABORT: no free GPU` (10-12 04:09 CDT) → 33 행 전제 검사 중단(`DECISIONS.md not tracked+clean`, 04:39) → 35 행 `--resume FXALDSRP` → 40 행 `SKIP: genie reference FXSRPB16e4 not accepted` → 43 행 `--resume FXSRPB16e4 FXALDSRP` → `ok=2`. FIGHSX16e4 §6.4 는 "재개 세 번", 예측 7 채점은 "시작 줄 3 개" 라고 적었다.
- 바꿀 문장: "FIGHSX16e4 는 마지막 행이 'no free GPU' 로 빠져 재개가 필요했고, 재개 시도가 세 번 들었다(FIGHSX16e4 §6.4)."
- 같은 칸에 운영 줄 하나: "재개할 때 기준 행에 기대는 행(FHSPDMI · FHALDDMI)은 기준 행과 함께 준다 — `--resume FHDMIB16e4 FHALDDMI`; 혼자 주면 203 행에서 SKIP 된다(`ACC` 는 호출마다 비어 있다)."

### S-3 사용자 지시의 귀속 — `DECISIONS.md` 줄이 없고, 스크립트 머리말은 DMI 에 대한 지시처럼 읽힌다
- 초안 머리말 둘째 항목의 굵은 문장("DMI 에 대한 별도 지시는 없다 — 이 세션의 해석")은 분명하다. 그러나 (a) `grep FIGHSDMI DECISIONS.md` 는 0 줄이고, 스크립트가 `DECISIONS.md` 의 추적·clean 을 요구하므로 줄은 실행 커밋에 넣어야 한다; (b) 스크립트 2–3 행은 `user 2026-10-11 CDT "…" / "…"` 만 적어 DMI 에 대한 사용자 결정으로 읽힌다; (c) 항목의 이름표가 "사용자 지시(…원문)" 이다.
- 고칠 것: (a) v2 커밋에 `DECISIONS.md` 줄(시각은 `date` 로): "FIGHSDMI16e4: DMI 그림의 +6..+15 dB 점을 새 시행 n = 20480 으로 (보고 전용) | **사용자의 별도 지시 없음 — 이 세션의 해석**: 10-11 CDT 의 두 지시('figure는 매끄러운 곡선이 나타나는게 좋아' · '다 보강하는게 좋을 거 같다' — 당시 대상은 SRB · SRP, DMI 는 철회 중)를 같은 상태인 DMI 그림에 적용. 그림 `F21dmi_col` 을 보내며 보강 준비를 알림(10-12 CDT); 사용자가 원하지 않으면 멈춘다. 틀 = FIGHSPATH16e4 v2; 판정·라벨 불변." (b) 스크립트 2 행의 괄호를 `(REPORT-ONLY figure supplement; NO separate user instruction for DMI -- the session's extension of the user's 2026-10-11 CDT "…" / "…", registration header)` 로(행 수를 늘리지 않게 2–3 행 안에서). (c) 이름표를 "근거(사용자 지시의 연장 — DMI 에 대한 지시는 없음)" 로.
- 프로젝트 규칙("고부하 작업은 실행 전 사용자에게 확인"): 초안에는 알렸다는 것만 있다. §5 에 "사용자 확인을 받았다 / 알리기만 했고 답이 없었다" 가운데 사실을 적는다.

### S-4 작성 시점 공개에 빠진 것 — 보강이 바꿔 그리는 "제안 곡선 이하" 점들과, 뒤따르는 결정의 선례
- ROOM16e4 §7.4: n = 2560 그림에서 점추정으로 제안 곡선 이하인 baseline 점이 12 개이고(모두 +6 dB 이상), 양쪽이 0 이 아닌 점은 **Annealed Langevin +6 dB (4 대 4)** 하나다. 보강 그림은 바로 이 +6..+15 dB 점들을 새 시행 값으로 바꿔 그린다. 초안의 공개는 V1 · b\* · genie 의 수만 적는다.
- 덧붙일 문장: "n = 2560 그림에는 점추정으로 제안 곡선 이하인 baseline 점이 12 개 있다(§7.4; 11 개는 양쪽 0 실패, 하나는 Annealed Langevin +6 dB 4 대 4). 보강 그림은 이 점들을 새 시행 값으로 바꿔 그린다 — 원 그림과 그 문장은 기록에 남고, 보강 기록(`paper_f21dmihs.txt`)의 같은 줄('at or below the proposed curve')을 §6 에 원문으로 옮긴다."
- §3 의 6 번(n = 81920 후속)은 결과를 보고 정하는 갈림길이다. 덧붙일 문장: "그 후속은 따로 등록하며(FIGHSX16e4 의 틀: n = 81920 raw 의 첫 20480 시행 = 이 실행의 시행), 이 실행의 +12 · +15 dB 점은 어느 쪽이든 기록에 남는다. 선례: SRB · SRP 에서는 n = 20480 결과를 본 뒤 FIGHSX16e4 를 돌렸고, +15 dB 결과를 본 뒤 사용자가 원고 그림을 +12 dB 까지만 그리기로 했다(`hsx12`; `DECISIONS.md` 10-12 CDT)."

### S-5 실행·재개 중 작업 트리 규칙이 빠져 있다 (§1 "순서·자원")
- 초안: "감사의 반영은 `FIGHS_DONE` 뒤에 커밋한다". 커밋만 미루고 작업 트리에서 `DECISIONS.md` 나 이 문서를 고치면 `--resume` 이 155 행에서 죽는다 — FIGHSX16e4 의 04:39 CDT 중단이 그 경우였다(위 S-2 의 33 행).
- 바꿀 문장: "감사의 반영은 마지막 `--resume` 이 끝날 때까지 **작업 트리에서도 하지 않는다**(`DECISIONS.md` · 이 문서 · `conf/code` · `Demo` 를 건드리지 않는다 — 스크립트의 154–156 행; FIGHSX16e4 의 04:39 CDT 재개 중단)."

## NIT

- **N-1** 스크립트 141 행 주석 "only a --resume gets here (a fresh run ABORTs on any ald_*_hisnr.npz)" 는 `# EARLY` 뒤에는 틀리다(새 실행의 단계 R 도 이 분기로 온다). 주석을 고치면 §1 의 차이 목록에 141 행을 더하고, 그대로 두면 §1 에 한 마디 적는다.
- **N-2** 이른 호출이 GPU 를 못 잡으면 로그에 `FHALDDMI ABORT: no free GPU … (resume later; no automatic retry)` 가 찍히고 바로 다음 줄이 "phase R tries once more" 다. §6 생성기는 "ABORT · SKIP · INVALID 줄" 을 센다 — §1 에 "이른 호출의 ABORT 줄은 행의 실패가 아니다; 예측 5 는 `start` 줄 1 개 + `FIGHS_DONE ok=3 fail=0` 으로 채점한다" 를 적는다.
- **N-3** "시행 0..2559 의 쌍과도 겹칠 수 있다" → "겹친다": 60,700 쌍에서 20,480 번 복원 추출이면 SNR 당 서로 다른 쌍의 기대값은 약 17,400 개, 같은 SNR 의 시행 0..2559 의 쌍을 다시 뽑는 시행의 기대값은 약 850 개다(계산: `review_FIGHSDMI16e4_check.out`). ALD · 희소 조정의 개발 채널도 같은 테스트 풀에서 나온다(ROOM16e4 §1 고유 사항 (6)) — "다른 스트림" 옆에 한 마디.
- **N-4** §3 의 6 번: "(예측이 아니라 …)" 문구는 분명하나 "미리 적는 예측" 의 번호 목록 안에 있다(FIGHSPATH16e4 의 채점은 "예측 여섯" = 1 · 2 · 3 · 4a · 4b · 5). 번호를 떼어 목록 아래 "메모(채점하지 않음)" 로 옮긴다. 1 · 2 · 3 번은 여러 칸의 묶음이니 "모두 성립해야 적중" 을 적는다.
- **N-5** 머리말 둘째 항목의 `"BLER 이 낮아 고SNR 점이 몇 건 / 0 건인 방 풀 그림"` 은 세션의 요약인데 "원문" 이름표 아래 따옴표로 묶여 있다 — 따옴표를 뗀다.
- **N-6** "언제 만들어도 같은 파일": 같은 HEAD · 같은 GPU 기종에서는 바이트까지 같다(npz 멤버 시각은 1980-01-01 고정, `prov` 에 git · 장치 이름 · `ald.py` sha). 다만 단계 C 의 추정기 대조가 보는 것은 시험 세트(배치 2560)이고, 새 시행 배치(20480)의 재현성은 결정적 설정과 `estimate` 안의 같은 시드 두 번 assert (첫 SNR)가 받친다 — 괄호의 근거를 그렇게 적는다.
- **N-7** §1 의 실행 명령에 tmux 세션 이름이 없다(5-DMI 는 `tmux new -d -s dmieval -c … "taskset … bash …"` 를 원문으로 적었다). §5 에 실행 명령 원문과, `HSREG` 변경이 ecaaf967 (실행 커밋 **앞**)에 들어갔음을 적는다.
- **N-8** 상속 메모(회귀 아님): `case` 줄은 조정 기록의 sha 를 보지 않고 추적·clean 만 본다(지금 sha 1e7824c1bae10376 = 5-DMI); 그림 기록 "Counts:" 줄의 `raw_<원 태그>` 꼬리표.

## 확인한 것 (방법)

1. **스크립트**: `bash -n` 통과. `diff <(sed 's/SRP/DMI/g; s/fighspath/fighsdmi/g; s/FIGHSPATH/FIGHSDMI/g' code/run_fighspath16e4.sh) code/run_fighsdmi16e4.sh` 의 묶음 = `2,7c2,10` · `17,19c20,22` · `168c171` · `191a195` — §1 이 적은 그대로다(2–10 · 20–22 · 171 · 195 행). 남은 SRP / PATH 값 없음(머리말의 부모 스크립트 이름뿐). 부모 `run_fighspath16e4.sh` sha e51214bd1b49a16d = 검토·실행된 파일.
2. **`ROWS` = 5-DMI = 디스크**: 체크포인트 dc784649f1e9b890; `repr(float(fit_DMI_Nr8_fullK1024_n160000.npz['ll_val']))` = `112.04253042212595`; `arms.gmm_selection("D2", "DMI", 8, 160000)` (fits dir `gmm_fits_D2_DMIB16e4`) → `gmm1024`, kron 최고는 2048 의 41.180 (후보 `.k0r*` 파일과 kron 4096 은 `load_fits` 가 읽지 않는다); pick 8f72c113efb91b0b 추적·clean, `per_snr` 에 6 / 9 / 12 / 15; `ald_PILDMI.npz` b0145dac7b7076aa, `pilots_PILDMI_test.npz` 1e8cc99169b3f18c, `pilots_PILDMI_dev.npz` 있음, `tune_PILDMI.json` 1e7824c1bae10376 추적·clean (ckpt = `$CK` 문자열, ckpt_sha, dev_skip 2560, n_dev 512, stop · v 에 6.0..15.0); 원 raw 셋의 `…snr{6,9,12,15}_skip0_n40.npz` 에 각 행의 arm × `KEYS_RAW` 전부, meta bstar gmm1024 / kron_K 2048 (키 있음) / ll_val / ntrain / 체크포인트 id (SP 는 없음) / `meta|sparse` == pick / `meta|ald_file`.
3. **`# PRE` 줄**: 지금 실패하는 것은 154 행(`conf/code` 에 미추적 스크립트) · 155 행(등록 미추적) · 156 행(HEAD 가 등록의 마지막 커밋이 아님) 셋 — 모두 실행 커밋이 해결한다. 157–159 행 통과(`raw_FH*DMI*` · `raw_FHC*DMI*` · `ald_PILDMI_hisnr.npz` · `pilots_PILDMI_hisnr.npz` · `FHC*DMI*` 대조 파일 · `fighs_FH*DMI*` · `logs/run_fighsdmi16e4.log` 없음), 행별 검사(165–174) 통과. `conf/code` · `Demo` 는 DMI 주 실행 커밋 4131a3b0 이후 바뀌지 않았다(`git diff --stat` 비어 있음).
4. **`# EARLY`**: (a) 새 실행에서 이른 호출이 `ald_PILDMI_hisnr.npz` 를 만들고(`_prov` 의 git = `git -C conf rev-parse --short HEAD` = 스크립트의 `$H`) 단계 R 이 141–143 행으로 재사용한다 — 그 분기의 한 줄 파이썬을 기존 `ald_PILSRP_hisnr.npz` 에 돌려 `c48ee796` 을 얻었고, 행 루프 모사에서 ALD 행 뒤의 행까지 4 / 4 행을 읽었다(`review_FIGHSDMI16e4_stdin_sim.out`; `python -c` · `nvidia-smi` 는 here-string 을 먹지 않는다 — `nvidia-smi` 는 따로 시험). (b) 빈 GPU 가 없으면 로그 두 줄 뒤 단계 R 이 한 번 더 한다. (c) 전역 `TAG CELL PR BF CK FL` 는 그 행의 `read` 값, `sel` 은 `--resume TAG…` 에서도 같게 걸린다; 재개에서는 추정이 있으면 "reusing" 이 두 번 찍힌다. 그 밖의 차이는 M-1 뿐이다. `ald.py regen --set hisnr --prior DMI --fits-tag DMIB16e4`: fits 가드(`fit_DMI_…fullK32…` 있음), SNR 6 / 9 / 12 / 15, skip 10000, n 20480, 시행 루프는 `runner.run_task` 와 같은 순서; 쓰는 rotation −1 / doppler −1 / train_prior DMI = 개발 파일럿의 것 → `_guard` 통과. `estimate`: 시드 `SEED + 1000 + 17k` 의 cuda Generator, 결정적 알고리즘, TF32 꺼짐. 수신기는 `ALDSitePrior.ep_site` 에서 시행마다 파일럿 사이트 b 를 대조한다.
5. **`eval_accept` 인자**: 스크립트가 내는 꼴(`--prior DMI --ntrain 160000 --bstar gmm1024 --ll-val … --tag <TAG>:<role>:<sha>:C2 [--ref-raw …]`, `--kron-K` 없음)을 원 raw 에 읽기 전용으로 돌렸다(n 2560, skip0 0): `DMIB16e4:best:dc78…` · `SPDMI:-:-` + `--ref-raw raw_DMIB16e4` · `ALDDMI:best:dc78…` + `--ref-raw` 모두 `ACCEPT: OK`; `--points C2:6,9,12,15` 를 주면 −3 / 0 / +3 이 남는다는 줄만 나온다(`review_FIGHSDMI16e4_accept_dry.out`). `run_fighsroom16e4.sh` 의 SRB 행과 같은 꼴(`gmm1024|-`).
6. **그림**: `hs_tag` → FHDMIB16e4 / FHSPDMI / FHALDDMI = 스크립트의 태그, 집계표 `fighs_<TAG>.txt`. `HSREG[PRIOR]` 는 `HS` 일 때만 평가된다. `FIG_OUTDIR=<스크래치>` 로 다시 그린 `DMI` · `SRB` · `SRB hs` 의 기록과 PDF · PNG 가 커밋본과 **바이트 동일**(9 파일; `conference/figures` 에 새로 쓰인 파일 없음 — `find -newer` 로 확인). `FIGHS_ALLOW_MISSING=1 … DMI hs` 시험 렌더: rc 0, WARNING 22 줄, 기록에 `NEXT_EXPERIMENTS_FIGHSDMI16e4 §1` 두 번, `F21dmihs_col.{pdf,png}`, y (3e-05, 1.2).
7. **사실 문장**: `pairB_SPDMI.txt` 의 판정점(R0-pilot@1 +3/+6/+9, R1-turbo 0/+3/+6, R3-bigamp +6/+9/+12, R4-llr +9/+12/+15, R4-scvamp +3/+6/+9, OMP-pilot 0/+3/+6, 나머지 10 개 −3/0/+3); §7.4 의 V1 4/0/0/0 · b\* 7/0/0/0 · genie 0/0/0/0, 0 실패 18 / 77 점; raw 다섯의 최대 skip 2520, `raw_DMI/` 빈 디렉토리; 시행 스트림 → 테스트 풀(`dmimo._which`), 풀 60,700 쌍, PID 14, `HISNR_SKIP0` 10000; `fighs_FHSRBB16e4.txt` V1 45/10/3/4, `fighs_FHSRPB16e4.txt` 45/7/0/0, `fighs_FXSRBB16e4.txt` 12 · 11, `fighs_FXSRPB16e4.txt` 4 · 1; `DMI_BASE_DONE` 18:15 CDT; runner 시간 39.0 · 41.6 · 46.6 · 28.3 · 14.9 · 10.4 분(로그) → 64.2 · 59.6 분, 합 약 2.4 시간; 메모리 264 GB 대 지금 가용 991 GB; 실행 커밋 c48ee796 · 193776a1.
8. **§3**: 1–5 번은 집계표·그림 기록의 'rising' 줄·`FIGHS_DONE` 줄로 채점된다. DMI 의 새 시행 산출물이 없는 상태에서 적혔다. 자명하지 않다 — 1 번은 SRB 의 결과(3 → 4)였다면 빗나갔고, 4a 는 n = 2560 의 0 건에서 나오지 않으며, 4b 는 SRB 에서 4 건이었다. 2 번과 5 번은 거의 확실한 쪽이다.
9. **CPU**: `jobs = min(os.cpu_count(), 작업 수)` — 단계 C 의 대조 runner 셋은 4 워커씩(12 프로세스), 단계 R 은 192 워커를 96 스레드에(워커당 BLAS 1 스레드; DMI 주 실행·baseline 이 같은 방식으로 448 / 448). `taskset` 목록 = NUMA 노드 1 · 3. 교착·메모리·결과에 걸리는 것 없음. 디스크 여유 3.3 TB, 지금 도는 runner 없음, GPU 여섯 장 비어 있음(검토 시점).

## 확인하지 못한 것

- GPU 단계 전부(`ald.py estimate --set hisnr` 의 DMI 실행, 추정기 대조의 비트 동일) — 코드로만 읽었다. 실행 시점의 빈 GPU.
- 수신기 대조(시험 청크 0 의 비트 동일)가 DMI 에서 통과할지 — runner 를 돌리지 않았다. 근거는 코드가 원 실행 커밋 이후 그대로라는 것뿐이다.
- 세션 기록 기준 진술: 그림을 사용자에게 보내고 보강 준비를 알렸다는 것, 작성자·사용자가 본 것의 범위, 사용자 인용의 원문.
- 함께 도는 기록 감사의 스레드 수·NUMA 노드, 감사가 작업 트리를 건드리지 않는다는 것(S-5).
- v2 커밋이 등록·스크립트·`DECISIONS.md` 줄만 담고 그 뒤 `FIGHS_DONE` 까지 커밋이 없다는 것.

## 이 검토가 쓴 파일 (모두 `prereg_reviews_2026-10-11/`)

`review_FIGHSDMI16e4.md` · `review_FIGHSDMI16e4_check.py` → `review_FIGHSDMI16e4_check.out` (값 대조 29 / 29) · `review_FIGHSDMI16e4_accept_dry.out` · `review_FIGHSDMI16e4_stdin_sim.py` → `review_FIGHSDMI16e4_stdin_sim.out`. 저장소의 다른 파일은 건드리지 않았다.
