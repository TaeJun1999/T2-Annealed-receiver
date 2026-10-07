# 적대적 검토 — NEXT_EXPERIMENTS_FIGHS16e4.md v1 (논문 BLER 곡선 고SNR 점, 새 시행 n = 20480, 보고 전용) + `code/run_fighs16e4.sh` (미추적) + `code/ald.py` `--set hisnr` 3 줄 (2026-10-06 18:50 CDT = 10-07 08:50 KST; Fable 5.1 서브에이전트, 읽기 전용)

읽기 전용 조사. `run_fighs16e4.sh`·runner·`ald.py` 는 **실행하지 않았고** GPU 도 쓰지 않았다 (시행 10000..30479 접근 0, `fhrev` 출력 0). 본 것: 등록 전문·스크립트 전문·`git diff -- code/ald.py`; 전례 `NEXT_EXPERIMENTS_HISNR16e4.md` v2·`run_hisnr16e4.sh`; 원 raw 를 만든 스크립트 `run_sparse16e4.sh`·`run_pilot16e4.sh`·`run_rot16e4.sh`·`run_supp16e4.sh`·`run_ald16e4.sh`·`run_static16e4.sh`; `runner.py` (chunk_plan·raw_file·build_point·run_task·cmd_run·main 가드·`_git_head`), `arms.py` (ALDSitePrior·`_ald_table`·pilot/sparse arm), `eval_accept.py`·`hisnr_report.py`·`analysis.load_raw`·`run_manifest.py`; `conference/figures/paper_f16·f17·f20·f21·f22·f24·f31.py`; 원 raw 28 개의 +6 dB 청크 0 메타 (`run|git`, `meta|stagec_ckpt_id`, `meta|sparse`, `meta|rotation`, `meta|ald_file`, `meta|pilot_arms`, arm 집합, bstar·kron_K·ll_val); ckpt 6·pick 6·ALD 기록의 sha256 과 git 추적 상태; `results/ald/*.npz` 의 skip·n (main + 워크트리 7); 전 트리 `raw*` 디렉터리 이름 전수; 원 raw 로그의 청크 시간. 스크래치 (지워도 됨): `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/fighs_review/{recount_0_4.txt, chunk_times.txt}`. 삭제 명령 없음.

**요지.** 충실도·시행 분리·수치 (§0.3 전수, §0.4 실패 수 76 곡선 전부, §1b 청크 시간 29 행, 화살표 상한, pick·ALD 튜닝 값) 는 모두 재계산으로 맞았다 (C 절). 고칠 것은 둘 다 "동결될 문장이 스크립트가 하는 일과 다르다"는 종류다: 집계표의 R0-pilot @1 열 (문서에 있고 스크립트에 없음), ALD 행의 대조가 "같은 수신기" 를 보인다는 문장 (추정기 `ald.py estimate` 는 대조되지 않음). 나머지는 전제 검사 보강과 그림 규칙의 열린 선택 (y 축 한계, 무효 태그 처리, Fisher 방향) 이다.

---

## A. MUST (동결 전 고침)

**MUST-1. 집계표의 R0-pilot @1 — 문서는 약속하고 스크립트는 내지 않는다.**
- 위치: 등록 §1 "보고" 행 (`NEXT_EXPERIMENTS_FIGHS16e4.md:70` "R0-pilot 은 @16 과 @1 둘 다") ↔ `code/run_fighs16e4.sh:128-129` (`counts`: `e = ...["blk_err"]...[:, -1]` 만, 반복 1 열 없음).
- 근거: `counts()` 는 모든 arm 을 `[:, -1]` (@16) 로만 집계한다. 범위 안 그림은 R0-pilot 을 @16 으로만 읽으므로 (`paper_f22.py:74-75` `fails` = `[:, -1]`; `paper_f21.py` 의 ARMS 는 모두 `it = -1`, R0-pilot 은 "(not drawn)" @16; F24 (c)(d) 는 R0-pilot 을 그리지 않음) @1 은 그림에 필요 없다. 그러나 동결 문장이 존재하지 않는 출력 열을 적으면 감사에서 편차가 된다.
- 고침 (둘 중 하나): (a) `run_fighs16e4.sh:129` 다음에 한 줄 추가 —
  `        if a == "R0-pilot": e1 = np.where(np.isfinite(v := np.asarray(d[k][a]["blk_err"], float)[:, 0]), v, 1.0); f1 = int(e1.sum()); lo1, hi1 = wilson(f1, n); print(f"SNR {k[2]:+.0f}  {'R0-pilot@1':<20} {f1:6d} / {n}  BLER {f1 / n:.2e}  95% [{lo1:.2e}, {hi1:.2e}]")`
  (b) 또는 §1:70 에서 "R0-pilot 은 @16 과 @1 둘 다" 를 지우고 "모든 arm @16 (그림의 읽기)" 으로.

**MUST-2. ALD 행 (18·21) 의 대조는 수신기만 검사하고 추정기는 검사하지 않는데, §1 은 "같은 수신기에서 나온다는 것" 을 보인다고 적는다.**
- 위치: 등록 §1 "대조" 행 (`:68` "ALD 행의 대조는 원 시험 ALD 추정 파일로 … 목적: … 같은 수신기 (현재 코드·같은 플래그·같은 arm 부분집합) 에서 나온다는 것") 과 §1a 행 18·21 (`:98`, `:101` "대조는 `ald_XAROTaB16e4k.npz` 4d05…"); 스크립트 `ctl` (`run_fighs16e4.sh:136` `sed 's/_hisnr\.npz/.npz/'`) 과 `ald_new` (`:138-148`).
- 근거: phase C 는 runner 를 **원 시험 추정 파일** (`results/ald/ald_XAROT{a,b}B16e4k.npz`, skip 0, 2026-09-29 d17f3d65 에서 GPU float32 로 계산) 로 돌려 ALDSitePrior + RouteA 가 비트 재현되는지만 본다. 새 점의 ALD-pilot 은 phase R 에서 **지금의** `ald.py estimate` (현재 GPU·torch·`_det()`) 가 새로 만드는 `ald_<T>_hisnr.npz` 를 읽는다. 추정기 쪽 (`ald_run`) 이 원 추정과 같은 결과를 내는지는 어디서도 비교되지 않는다 — `cmd_estimate` 의 결정성 검사 (`ald.py:267-271`) 는 같은 실행 안의 같은 시드 2 회뿐이고, `_ald_table` 의 ckpt sha 검사와 `tune` 포함은 입력 동일성만 본다. 두 시행 집합을 한 ALD 곡선으로 잇는 근거가 다른 arm 보다 약한데 문장은 같다.
- 고침 (둘 중 하나; (a) 권장, 비용 GPU 수 분):
  (a) `ctl` 에 추정기 대조 추가 — ALD 행이면 runner 전에: 동결 기록을 스크래치 태그로 복사 (`cp -n results/ald/tune_$T0.json results/ald/tune_$C.json; cp -n results/ald/pilots_${T0}_dev.npz results/ald/pilots_${C}_dev.npz; cp -n results/ald/pilots_${T0}_test.npz results/ald/pilots_${C}_test.npz`, `T0` = 행의 ALD 태그, `C` = `FHC…`), 빈 GPU 1 장에서 `CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag $C --ckpt $CK --set test` 를 돌리고, `np.array_equal(np.load("results/ald/ald_$C.npz")["hhat"], np.load("results/ald/ald_$T0.npz")["hhat"])` (b·v 도) 를 `$OUT/${C}_aldcontrol.txt` 에 `CONTROL-ALD: OK|FAILED` 와 최대 |차| 로 적는다; `:192` 의 게이트에 `grep -qx 'CONTROL-ALD: OK'` 를 함께 건다. (`cmd_estimate` 의 `a.ckpt == rec["ckpt"]`·`ckpt_sha` assert 는 복사한 기록으로 그대로 통과한다.) §1:68 에 "ALD 행은 수신기 대조 (원 시험 추정 파일 입력) + 추정기 대조 (시험 집합 재추정 hhat 비트 동일)" 로 적는다.
  (b) 또는 §1:68 과 §1a:98·101 을 "ALD 행의 대조는 **수신기만** (원 시험 추정 파일을 입력으로; 추정기 `ald.py estimate` 의 재현은 검사하지 않는다 — 새 추정 파일의 `prov` (git·ald_py_sha·device·precision) 와 원 파일의 `prov` 를 §6 에 나란히 적는다)" 로 고쳐 과장을 없앤다.

---

## B. SHOULD

**S-1. 원 시험 ALD 추정 파일·개발 파일럿의 sha 를 전제에서 검사하지 않는다.** `run_fighs16e4.sh:166-167` 은 `ald_$t.npz`·`pilots_${t}_dev.npz` 의 존재와 `tune_$t.json` 의 tracked·clean 만 본다. §1a 는 4d053e3e69cea6ce·1ea34f2fb53df32c 를 적어 두었으나 (지금 값과 일치: 확인) 파일이 바뀌어 있으면 대조가 "FAILED" 로 돌아 행만 빠지고 원인이 전제가 아닌 대조 실패로 적힌다. 고침: `:167` 에 `case $t in XAROTaB16e4k) s=4d053e3e69cea6ce;; XAROTbB16e4k) s=1ea34f2fb53df32c;; esac; [ "$(sha256sum results/ald/ald_$t.npz | cut -c1-16)" = "$s" ] || die "$TAG: ald_$t.npz sha != $s"` 추가; §5 에 `pilots_XAROT{a,b}B16e4k_dev.npz` sha256[:16] (지금 64939076f196f810 · 2032a1c8ea447159) 도 적는다. 또한 §1:74 "ALD 기록 tracked" 는 `tune_*.json` 만 참이다 (`ald_*.npz`·`pilots_*_dev.npz` 는 `??` 미추적) → "tune 기록 tracked; 추정·파일럿 npz 는 미추적 (sha 를 §5 에)" 로.

**S-2. `_hisnr.npz` 가 이미 있으면 출처 확인 없이 재사용한다.** `run_fighs16e4.sh:141` `[ -f $E ] && return 0`; 전제 `:154` 는 `raw_FH*` 만 본다. 다른 커밋에서 만들어진 잔존 추정 파일이 있으면 새 실행이 그것을 쓰고, `_ald_table` 은 ckpt sha 만 검사한다. 고침: 전제에 `[ $RESUME = 1 ] || [ -z "$(ls results/ald/*_hisnr.npz 2>/dev/null)" ] || die "stale *_hisnr.npz"`; `ald_new` 의 재사용 분기는 `[ -f $E ] && { [ "$($P -c "import json,numpy as np;print(json.loads(str(np.load('$E')['prov']))['git'])")" = "$H" ] && return 0 || { log "$TAG ABORT: $E made on another commit"; return 1; }; }` 로.

**S-3. 그림 규칙의 y 축 아래 한계가 열려 있다.** `:71` "y 축 아래 한계는 n = 20480 점이 보이도록 낮춘다" — 값이 없다. n = 20480 의 0 점 화살표 끝 1.9e-4 는 지금 F20 (b)·F21·F22·F24 의 2e-4 **아래**이고 최소 비영 BLER 4.9e-5 도 그렇다 → 어떤 값으로 낮출지는 실행 뒤 선택이 된다. 고침 (예): "F16 (a)·F20 (b)·F21·F22·F24 (c)(d)·F31 (b) 의 아래 한계 = 3e-5 (4.9e-5 와 1.9e-4 가 모두 보이는 가장 가까운 3·1 격자값); F17 은 4e-5 유지" 로 지금 적는다.

**S-4. 무효·미실행 태그가 생겼을 때 그림이 무엇을 그리는지 없다.** `:69` 는 "그 태그 무효·집계표 없음" 까지, `:71` 은 모든 곡선이 새 raw 를 쓴다고만 적는다. 고침: `:71` 에 "무효 (수용 실패)·미실행 (대조 실패·REF 미수용) 태그의 곡선은 원 raw (n = 2560) 점 그대로 두고 캡션·그림 기록에 '이 곡선은 전 구간 n = 2560' 을 밝힌다; 재실행은 사용자 승인 뒤 (그때까지 그림을 반쯤 바꾸지 않는다)".

**S-5. Fisher p 의 대립가설·표가 정해져 있지 않다.** `:71` "그 칸의 단측 Fisher p (SNR 점마다 독립 시행)". 고침: "표 [[f_hi, n_hi − f_hi], [f_lo, n_lo − f_lo]], 대립가설 = 높은 SNR 의 BLER 이 더 크다 (`scipy.stats.fisher_exact(..., alternative='greater')`); 오르는 칸 = 실패 수가 직전 SNR 보다 **큰** 칸 (동률 아님); 오르는 칸마다 그림 기록 텍스트에 반드시 적고 캡션은 선택". ("필요하면 캡션" 의 '필요' 도 지금 정하거나 기록 텍스트로 한정.)

**S-6. 스크립트에만 있는 규칙 둘을 §1 에 올린다.** (i) `run_fighs16e4.sh:193` — REF 행이 수용되지 않으면 종속 행 (SP/PIL/XP/XA) 을 **돌리지 않고** SKIP (FAIL 집계); `--resume` 부분 집합은 REF 행을 포함해야 한다 (스크립트 머리말 `:16-17` 에만 있음) → §1:75 중단·재개에 한 문장. (ii) `:75` "ALD 2 행은 §4 결정에 따름; 동결 전에 정한다" 는 결정이 났으므로 (§4 2026-10-06 18:33 CDT 넣는다) "ALD 2 행 포함" 으로 바꾼다.

---

## C. NIT

- **N-1** §0.1:14 첫 행은 패널 5 개의 **합집합**을 arm 열에 적었다 (R1·R3 는 F21 (a) 만; F16 (a)·F17 (a)·F22 (a)·F31 (b) 는 그리지 않음; F17 (a)(b) 는 b\*·V1·genie 만, `paper_f17.py:61-63`). "패널별 합집합" 이라고 한 단어 넣거나 행을 나눈다.
- **N-2** §3:146-147 의 "(ALD 행이 빠지면 296 / 68)" 과 §0.1:27 "(ALD 행이 빠지면 74)" — ALD 포함이 결정됐으니 지운다.
- **N-3** §4:154 "잔여물 (주 세션이 지울 것)" — 확인 시점에 `raw_fhsmk*`·`results/gmm_fits_D2_fhsmk*`·`run_manifest_fhsmk*`·`results/ald/*fhsmk*` 모두 **없음** → "삭제 확인 (시각)" 으로.
- **N-4** 대조 산출물이 §1 에 이름이 없다: `raw_FHC*` 24 디렉터리 (각 4 청크, 시행 0..39), `results/review_next/FHC*_control.txt` 24, `logs/run_D2_FHC*.log` 24, 링크 `results/gmm_fits_D2_FH*`·`FHC*` 48 → §1 "실행" 또는 §5 에 적는다 (HISNR 감사가 링크를 따로 적었던 전례).
- **N-5** `run_fighs16e4.sh:200` `run_manifest.py` 의 rc 를 기록하지 않는다 → `|| log "$TAG run_manifest rc=$?"`.
- **N-6** `ctl` (`:136-137`) 에서 runner 가 실패하면 `$L` 에 줄이 없고 나중에 SKIP 만 보인다 → `|| log "$TAG control runner failed ($LOGD/run_D2_$C.log)"`.
- **N-7** `cmp_arms` (`:81`) 는 청크 파일이 하나라도 있으면 통과 조건에 든다 → `len(fs) == 4` (SNR 당 1) 를 함께 요구.
- **N-8** `ald.py` 의 Langevin 시드는 **SNR 인덱스**에 매인다 (`SEED + 1000 + 17 k`, `ald.py:262`): hisnr 의 k = 0 (+6 dB) 는 시험 집합의 −3 dB 시드와 같다. 새 시행이라 통계적 결과는 없으나 §5 에 한 줄 (다른 SNR 의 추정과 시드가 겹친다는 것) 을 적어 두면 뒤에 묻지 않는다.
- **N-9** 집계표의 Wilson 은 `hisnr_report.wilson` (z = 1.959964), 그림은 자체 `wilson(z = 1.96)` (`paper_f16.py:73`) — 구간의 넷째 자리가 다를 수 있다. 그림 스크립트의 assert 는 실패 수만 비교하므로 무해; 기록에 한 줄.
- **N-10** §3: 예측 1–3 의 분모는 "실행·수용된 곡선만" 으로 채점한다고 적고 (행이 빠지면 304·70·24 가 줄어든다), 예측 2 의 "오르는 칸" 정의를 S-5 와 같이 "직전 SNR 보다 큰 실패 수" 로 명시.
- **N-11** `runner._git_head()` (`runner.py:470-477`) 는 워커마다 한 번 계산해 캐시한다 — 긴 행 (SPNR16 ≈ 168 min) 중간에 conf/code 가 더러워져도 그 워커의 뒤 청크 `run|git` 에 `+dirty` 가 붙지 않을 수 있다. 이 스크립트의 결함은 아니고 (f) 와 `:191` 이 HEAD 이동은 잡는다; 알고만 둔다.
- **N-12** `:142` `ald.py -h | grep -q hisnr` 는 실행 커밋에 ald.py 변경이 들어가면 늘 참 — 남겨도 무해.

---

## D. 확인되어 문제 없는 것

1. **충실도 (§1a 24 행 ↔ 원 raw).** 원 raw 28 개의 +6 dB 청크 0 메타와 생성 스크립트를 대조: ckpt sha·role (4443921ce8d5c4a1 legacy-last / 7ebf… best / d2d7… best / 6f3a… best / b591… best / c050… best) 와 b\*·kron_K·ll_val (kron 1024 −11.459169831224418; kron 4096 0.08879931165293979 / 5.797910431000217 / 33.7604873920761 / 63.1751571838059; SV8e gmm256 −47.80545576704972) 전부 일치; SP 원 raw 6 개는 `meta|stagec_ckpt_id` 없음 (`--stagec-ckpt` 없이, `run_sparse16e4.sh:246`) ↔ ROWS CK `-` ✓; PIL 원 raw 는 `--stagec-ckpt --pilot-arms` ✓; XP/XA 원 raw 는 `$B --pilot-arms` / `$B --ald-file` (`run_supp16e4.sh`) ✓; `meta|rotation` deg=15.0/30.0, `meta|ald_file` sha 4d05…/1ea3… ✓; 적합 링크 BF = 원 raw 의 fits (B16e4k·D3B16e4·SVB16e4·U28B16e4·MXB16e4·NR16B16e4) ✓; pick sha 6 개 = 파일 (tracked·clean) ✓ 이고 §1a 의 +6..+15 dB (ρ_SBL, ρ_OMP; n_em/L) 값 6 묶음이 pick JSON 과 일치 ✓; ALD 튜닝 c 0.01·β 0.005·멈춤 434/536/600/600·428/535/600/600 = `tune_XAROT{a,b}B16e4k.json` ✓ (tracked·clean, dev_skip 2560·n 512·rotation 15/30·ckpt_sha 4443…). ORIG 선택 (회전 루프 행 = ROT + XL 두 raw) 과 arm 보유도 맞다. 체크포인트 6 개 sha = §1a ✓.
2. **그림 ↔ raw ↔ arm (§0.1).** `paper_f16.py` (a) R2·b\*·V1·genie (Wilson) + SP 3 (막대 없음, raw_SPB16e4k); `paper_f17.py` b\*·V1·genie 만 (→ HISNR raw 로 덮임 ✓); `paper_f20.py` (b) raw_U28B16e4 의 b\*·V1·R2·genie (Wilson); `paper_f21.py` R3·R1·R2·b\*·V1·genie + SP 3, genie 0 점 화살표; `paper_f22.py` R0-pilot(@16)·bstar-pilot·V1-pilot·b\*·V1·genie; `paper_f24.py` (c)(d) R3·R1·R2·ALD-pilot·V1-pilot·b\*·V1·genie (ALDv 아님, 화살표 없음); `paper_f31.py` (b) V1·b\*·SP 3·genie (막대 없음). y 아래 한계 1.5e-4 / 4e-5 / 2e-4 / 2e-4 / 2e-4 / 2e-4 / 5e-4 = §1:71 ✓. 0 점 화살표 상한 z²/(n+z²) = 1.498e-3 (2560) · 1.875e-4 (20480) ✓.
3. **시행 분리 (§0.3).** 8 트리의 `raw*` 406 디렉터리·청크 164,302 개 이름 전수: [10000, 30480) 와 겹치는 것은 `raw_HSB16e4k`·`raw_HSNR16` 각 2048 (10000..30440) 뿐, 30480 이상 0, 10000 미만 최대 끝 5760 — 문서와 숫자까지 같다. `results/ald/*.npz` 의 (skip, n) 은 main·wtB·wtC·wtS 모두 (0, 2560)·(2560, 512) 뿐. 스모크 raw 는 없고 (삭제됨), `_skip1xxxx_` 를 담은 로그는 `run_D2_HSB16e4k.log`·`run_D2_HSNR16.log` 뿐. 회전은 `gen.rot` 만 바꾸고 스트림 소비 (`sample`→`integers`→`permutation`→`transmit`) 는 runner 와 `ald.py._regen_one` 이 같다 ✓.
4. **같은 시행·genie 짝.** 원 raw 에서 B16e4k = SPB16e4k = PILB16e4k, NR16B16e4 = SPNR16 = PILNR16, ROTa = XLROTa = XPROTa = XAROTa, ROTb = …(genie blk_err 비트 동일, +6..+15) ✓; B16e4k ≠ ROTaB16e4k (기대대로) → REF 선택 (D2 = HS raw, 새 데이터셋·회전 = 첫 행) 이 맞고 회전 행을 정적 genie 와 대조하지 않는 것도 맞다. `eval_accept --ref-raw` 는 모든 공유 시행 × 4 키, `shared == n` 요구 ✓.
5. **대조 (phase C) 설계.** `--n 40` (skip0 0) → 청크 이름 `_skip0_n40` = 원 청크 0 ✓; `cmp_arms` 는 arm × `KEYS_RAW` 7 키 (연속값 포함) 를 NaN=NaN 으로 비교 ✓; `sed 's/[^,]*/raw_&/g'` 는 "raw_ROTaB16e4k,raw_XLROTaB16e4k" 를 만든다 (확인) ✓; `${TAG/FH/FHC}` ✓. 단, ALD 행은 MUST-2.
6. **스크립트 논리.** `read -r` + IFS='|' 로 빈 FLAGS·공백 있는 ARMS 처리 ✓; `sel` 의 공백 경계 ✓; 모든 루프 안 python 호출에 `< /dev/null` 또는 heredoc ✓; `[ $RESUME = 1 ] && $P - <<PY | tee` 의 결합 ✓; HEAD = `git log -1 -- REG` 검사·행마다 HEAD 재검사·`run|git` ≠ H → (f) FAILED ✓ (`git rev-parse --short` 는 runner 와 같은 호출이라 길이 일치); 잘린 청크 → `.truncated/` 이동 후 runner 가 건너뜀 ✓; `--resume` 는 같은 커밋의 start 줄 요구 ✓; `exit $FAIL` ✓; `acc_extra` 의 `meta|sparse`·`deg=15.0:`·`meta|ald_file` 문자열 비교는 runner 가 쓰는 형식과 같다 ✓; `counts` 는 raised 를 실패로 ✓. 192 워커 × ALD 표 ≈ 85 MB = 16 GB ≪ 1 TB ✓.
7. **`ald.py` 변경.** regen: hisnr → SNR 6/9/12/15, skip 10000, n 20480, `pilots_<T>_hisnr.npz` ✓; dev/test 경로 문자 그대로 불변 ✓; estimate `--set hisnr` → `rec["stop"]["6.0"…]` 키 존재 ✓, `_guard` src == dev (rotation 15.0·S2·−1.0) ✓, 출력 `ald_<T>_hisnr.npz` (skip 10000) ✓; runner `_ald_table` 은 SNR 로 k 를 찾고 `ALDSitePrior.skip = 10000` → `tr = CURRENT_TRIAL − 10000` ✓ (b 대조로 어긋남은 예외 = 실패로 분류). `ald_new` 의 태그 추출·`--rotation 15`·`--fits-tag B16e4k` (fit_S2_ 가드) ✓; `--ald-file` 은 `--stagec-ckpt` 를 요구 (`runner.py:1323`) — 행 18·21 은 CK 있음 ✓.
8. **수치.** §0.4 의 76 곡선 × 4 실패 수 **전부 일치**, ↑ 15 (R3 6, 비 R3 9) ✓. §1b 청크당 s = 원 로그 +6..+15 평균 (SPB16e4k 253.5, PILB16e4k 32.0, XLROTaB16e4k 32.3, ROTaD3 387.0, XLROTaD3 87.3, SPD3 248.8, PILD3 87.3, ROTaSV 180.7, XLROTaSV 24.4, SPSV 154.9, PILSV 70.3, ROTaU28 406.6, XLROTaU28 121.8, SPU28 105.5, PILU28 170.4, ROTaMX 406.6, XLROTaMX 124.8, SPMX 179.2, PILMX 166.7, ROTa 208.6, XPROTa 29.8, XAROTa 7.5, ROTb 209.1, XLROTb 32.0, XPROTb 33.4, XAROTb 7.5, PILNR16 174.4, XLROTaNR16 314.2, SPNR16 942.7; HSB16e4k 243.0, HSNR16 2745.0) ✓; 묶음 합 (57/146/78/248/250/51/51/255 → ≈ 1136 + 15) ≈ 19.2 h ✓ (반올림 차 1 min). 38.901 재생성 몫은 유휴 측정이라 전부 부하 1.5–2 배 공개 ✓.
9. **예측.** 1·3 은 적정 (단, N-10 의 분모 문장); 2 는 S-5 의 정의로 닫힌다.
10. **문구.** §2 보고 전용 범위 문장 ✓; 해석 문장 없음 ✓; HISNR 틀 (skip0 10000·n 20480·chunk 40·`eval_accept --skip0/--points`·`run_manifest` 분할 문구) 그대로 ✓.

MUST count = 2

---

## Round 2 — v2 델타 재검토 (2026-10-06 19:26 CDT = 10-07 09:26 KST; Fable 5.1 서브에이전트, 읽기 전용)

본 것: v2 등록 전문 (204 줄; '검토 반영' 표의 줄을 표가 아니라 본문에서 확인), `code/run_fighs16e4.sh` 251 줄 전문 (`bash -n` 통과 확인), `git diff -- code/ald.py` (4 hunk), `ald.py` `cmd_regen`·`cmd_estimate`·`_prov`·`_guard`·`ald_run` keep 저장, `analysis.load_raw` 별칭 (`:183-186`), `runner._git_head`·`meta|ald_file` 형식·`ALDSitePrior.skip`, `common.HISNR_SKIP0`, 원 ALD 파일의 dtype·`prov` (`ald_XAROTaB16e4k.npz`: b·hhat complex128 (7, 2560, 32), v float64, prov JSON `git` = short), `tune_XAROTaB16e4k.json` 의 `ckpt`·`stop` 키, sha 6+2 개 재계산, tracked 상태, 스모크 잔여물 유무 (`raw_fhsmk*`·`results/ald/*fhsmk*`·`*FHC*` 모두 없음), `cp --update=none` 지원 (coreutils 9.4), `wc -w`·`nvidia-smi` 출력 형식. 실행·GPU·삭제 없음; 시행 10000..30479 접근 0.

### A. 1 라운드 MUST·SHOULD 해소 여부 (바뀐 줄로 확인)
- **MUST-1 해소 (b).** §1 보고 `:95` 에서 약속 문장 삭제, "모든 arm 은 @16" + 별칭 메모. 작성자의 정정은 맞다: `load_raw` 는 `d["R0-pilot@1"] = {q: a[:, :1]}` (`analysis.py:185-186`) 로 (n, 1) 열을 넣으므로 `counts()` 의 `[:, -1]` 은 그 줄에서 반복 인덱스 0 을 읽는다 — 라벨과 값이 맞고, 1 라운드의 "스크립트가 내지 않는다" 는 이 별칭을 놓친 것이었다. 등록 문장·스크립트·그림 읽기 (@16) 세 가지가 이제 일치.
- **MUST-2 해소 (a).** `ald_ctl` (`run_fighs16e4.sh:144-169`): 동결 기록 3 개 복사 (`:147`) → 빈 GPU 선택 (`:148-149`) → `ald.py estimate --tag FHC… --ckpt $CK --set test` (`:151`) → hhat·b·v `np.array_equal` + 최대 |차| → `CONTROL-ALD: OK|FAILED` (`:153-168`); phase R 게이트 `:233`. 코드 쪽 전제 전부 확인: `cmd_estimate` 는 `tune_{a.tag}.json`·`pilots_{a.tag}_{set}.npz`·`pilots_{a.tag}_dev.npz` 를 태그로 읽고 **`rec["tag"] == a.tag` 를 검사하지 않으므로** 복사 기록으로 돈다 (`ald.py:249-256`); assert 는 `a.ckpt == rec["ckpt"]` (`ckpt/d2sx_N160000_a1.pt` = 행의 CK, 상대경로, cwd = conf) 와 ckpt_sha 뿐; 출력은 `--set test` 면 `ald_<tag>.npz`, 아니면 `ald_<tag>_<set>.npz` (`:275`) — `ald_ctl` 의 `ald_$C.npz` 와 `ald_new` 의 `ald_<T>_hisnr.npz` 둘 다 맞다. 비교 heredoc 의 `a[k] - b[k]` 는 complex128·float64 라 안전 (bool 아님). 추정기 쪽 나머지 경로 (`regen` 의 새 시행 생성) 는 runner 의 `ALDSitePrior` 가 시행마다 저장 b = 수신 b 를 검사해 (`arms.py:187`) 불일치가 raised = 실패로 드러나므로 대조 틈이 없다. §1 대조 문장 ("수신기 대조 + 추정기 대조") = 스크립트 ✓. §0.5 의 동결 전 확인 (두 파일 비트 재현) 과 주 세션 증거 일치.
- **S-1 ✓** `:202-206`: 원 시험 추정 sha (4d053e3e69cea6ce·1ea34f2fb53df32c = 지금 파일) + dev·test 파일럿 존재 + tune tracked·clean; §5 의 파일럿 sha 4 개 (64939076f196f810·2032a1c8ea447159·844d55939b7bb55a·e6c68c6af0f7b72a) 와 tune sha 2 개 (6dd071bcd697d5d2·46da6a9477252a72) 모두 재계산 일치; §1 실행의 "tune tracked·clean, npz 는 sha" 문구 ✓.
- **S-2 ✓** `:190` 새 실행에 `ald_*_hisnr.npz` 있으면 ABORT; `ald_new :173-177` 재사용은 `prov.git == $H` 일 때만 (`_prov.git` 은 `rev-parse --short` 만이라 `+dirty` 로 어긋날 일 없음, `ald.py:155`). `ald_FHC….npz` 는 `_hisnr` 가 아니라 `:190` 과 충돌 없음 ✓.
- **S-3 ✓** `:96` 3e-5 (F17 4e-5 유지). **S-4 ✓** `:96` 무효·미실행 곡선 = 전 구간 n 2560 + 명시. **S-5 ✓** `:96`·§3 `:173` (아래 편차 2). **S-6 ✓** `:100` REF 미수용 → SKIP, 재개 부분집합에 REF 포함, "ALD 2 행 포함".
- NIT 반영 확인: N-1 `:38` ✓, N-2 (`:51`·`:171` 에 괄호 문장 없음) ✓, N-3 `:180` 끝 ✓ (잔여물 실제 없음), N-4 `:99`·`:195` ✓, N-5 `:241` ✓, N-6 `:142` ✓, N-7 `:69,83`·`:143` (`$(wc -w <<< "$SNRS")` = `4`) ✓, N-8 `:196` ✓ (k 매핑 서술 정확), N-9 `:95` ✓, N-10 `:171-173` ✓, N-11 `:85` ✓, N-12 가드 삭제 ✓.

### B. 두 편차
1. **`ald_ctl` 을 phase C 의 별도 순차 루프로 (`:224`) — 타당.** 수신기 대조 `ctl` 은 `sed 's/_hisnr\.npz/.npz/'` (`:141`) 로 **원** 시험 추정 파일을 입력으로 쓰므로 `ald_ctl` 의 산출물에 의존하지 않는다 → 순서를 떼어도 의미 변화 없음. GPU 선택이 `nvidia-smi memory.used < 100` 스냅샷이라 병렬이면 두 행이 같은 GPU 를 집어 Exclusive_Process 에서 하나가 죽는다; 순차면 앞 프로세스 종료 뒤 다시 조회 ✓. 비용 ≈ 2 × (모델 로드 + 35 s). 루프 안 stdin 소비도 없음 (`estimate … < /dev/null`, heredoc, here-string).
2. **S-5 "오르는 칸" 을 BLER 로 — 타당.** n 이 같은 칸에서는 실패 수 비교와 동치, 다른 칸 (+3 → +6, 2560 → 20480) 에서는 실패 수 비교가 무의미하므로 BLER 이 올바른 일반화; 동률 제외·표·대립가설 고정 ✓. §3 예측 2 는 +6..+15 만 세고 (§0.4 기준 9/70 도 그 구간) §1 규칙은 +3 → +6 도 기록한다 — 서로 모순은 아니다 (N2-5).

### C. 새 발견

**MUST — 없음.**

**SHOULD**

**S2-1. 대조 함수의 조기 반환이 묵은 판정 파일을 남겨 게이트를 통과시킬 수 있다.** `ctl :141-142` 는 runner 실패 시 `cmp_arms` 가 `$OUT/${C}_control.txt` 를 쓰기 **전에** `return 1`; `ald_ctl :149·:152` 도 GPU 없음·estimate 실패 시 heredoc 이 `_aldcontrol.txt` 를 쓰기 전에 `return 1`. 전제 `:189-190` 은 `raw_FH*`·`ald_*_hisnr.npz` 만 보고 `results/review_next/FHC*`·`results/ald/*FHC*` 는 보지 않으므로, 앞선 실행의 `CONTROL: OK` / `CONTROL-ALD: OK` 가 남아 있으면 (예: 승인된 재실행에서 raw 만 지운 경우) 대조가 돌지 않은 행이 `:232-233` 을 통과한다 — 대조가 보장하려는 문장이 조용히 무너진다. 고침 (2 줄): `ctl` 의 `local C=…` 다음에 `: > $OUT/${C}_control.txt`, `ald_ctl` 의 `local …` 다음에 `: > $OUT/${C}_aldcontrol.txt` (조기 반환이면 빈 파일 → `grep -qx` 실패 → SKIP). 더하여 (권장) `:190` 다음 전제 한 줄: `[ $RESUME = 1 ] || [ -z "$(ls $OUT/FHC*_control.txt $OUT/FHC*_aldcontrol.txt results/ald/*FHC* 2>/dev/null)" ] || die "stale FHC control artefacts"` — 이 줄은 `:147` 의 `cp --update=none` 이 묵은 FHC 사본을 그대로 두는 유일한 경로도 막는다.

**NIT**

- **N2-1** `--resume` 부분집합에 REF 행이 빠지면 머리말 `:18-19` 의 규칙과 달리 막지 않고 종속 행이 SKIP (안전하지만 재개를 한 번 더 하게 된다). 고침: 전제 루프 `:201` 다음에 `[[ $REF != FH* ]] || sel $REF || die "$TAG: the TAG subset must include its REF row $REF"`.
- **N2-2** 추정기 대조의 입력 `pilots_XAROT{a,b}B16e4k_test.npz` 는 `:204` 에서 존재만 본다 (sha 는 §5 기록). 바뀌어 있으면 `CONTROL-ALD: FAILED` 로 나와 원인이 전제가 아닌 "추정기 비재현" 으로 적힌다 (S-1 과 같은 종류). 고침: `:203` 의 `case` 에 `p=844d55939b7bb55a` / `p=e6c68c6af0f7b72a` 를 더하고 `:204` 에 `[ "$(sha256sum results/ald/pilots_${t}_test.npz | cut -c1-16)" = "$p" ]` 추가.
- **N2-3** 새 시행 ALD 추정의 실제 크기 (스텝당 20480 사이트 × 4 SNR) 는 돌려 본 적이 없다 (스모크 n 40, `:179`). `ald_run` 은 `keep` 스텝만 저장하므로 (`ald.py:111·139`) 메모리는 시험 집합의 ≈ 8 배 배치뿐 — 96 GB 에서 문제 없고 실패해도 `:183` 에서 행 18·21 만 SKIP — 그러나 §4 에 "n 20480 추정은 미스모크" 한 구를 적어 스모크된 것으로 읽히지 않게.
- **N2-4** `:147` `cp --update=none` 은 지키는 것이 없다 (FHC 사본은 이 스크립트만 만들고 원본은 sha·tracked 검사됨) — `cp -f` 가 더 단순하고 묵은 사본에 면역. S2-1 의 전제 줄을 넣으면 그대로 둬도 무해.
- **N2-5 (문서)** §1 그림 규칙은 +3 → +6 dB (두 시행 집합의 접합) 의 오름도 Fisher p 로 적고, §3 예측 2 와 §0.4 기준 9/70 은 +6..+15 만 센다. 모순은 아니지만 §3 `:173` 에 "(+3 → +6 칸은 기록만, 예측 2 의 분자에 넣지 않는다 — 기준 §0.4 가 +6..+15)" 한 구를 넣으면 뒤에 묻지 않는다.

### D. 새 스크립트 논리 — 확인되어 문제 없는 것
`ald_ctl`: `T0` 추출 (`grep -o 'ald_[A-Za-z0-9]*_hisnr'` 는 경로의 `ald/` 에 걸리지 않고 한 번만 매치) ✓, `printf tune_%s.json` 류 ✓, 반환값은 루프에서 무시되고 게이트가 파일로 판정 ✓, `estimate` 가 `ald_FHC….npz` 를 덮어쓰므로 재개 때 재계산 ✓, 모양 다르면 뺄셈 없이 FAILED ✓. `ald_new`: `E`·`T`·`V` 추출 ✓, `if [ -f $E ]` 분기의 `&& {…; return 0;} || {…; return 1;}` ✓, regen (`CUDA_VISIBLE_DEVICES=`) → estimate (`=$G`) → `[ -f $E ]` 체인 ✓, `cmd_regen` 의 hisnr 표 `(C.HISNR_SKIP0, 20480)`·SNR 6/9/12/15·`np.savez` 덮어쓰기 ✓, `--fits-tag B16e4k` 가드 (`fit_S2_`) ✓. 전제: `:186-194` 순서 (HEAD 검사 → raw → hisnr npz → `H` → resume start 줄 → HISNR 2048 → 행 이름) ✓; `:202-206` 의 `A || { … } || die` 결합과 `{ }` 의 종료 상태 = 마지막 `[ ] && …` 체인 ✓, `*) s=unregistered` 로 미등록 태그 거부 ✓. 게이트 `:232-233`: `${TAG/FH/FHC}` 는 모든 태그에서 선두 `FH` 만 치환 ✓; `grep -qx 'CONTROL: OK'` 와 `'CONTROL-ALD: OK'` 는 서로 매치되지 않고 `FHC*_control.txt` 글롭은 `_aldcontrol.txt` 를 잡지 않음 ✓. REF 순서 (4→5·6, 7→8·9, 10→11·12, 13→14·15, 16→17·18, 19→20·21) 와 `ACC` 미설정 → SKIP ✓. `cmp_arms` 청크 수 인자 4 ✓ (`len(fs) == nf and n > 0 and not bad`). `acc_extra` 의 `meta|ald_file` 형식 = runner `:455` ✓. `_git_head` 의 `+dirty` 는 `code`·`../Demo` 만 보므로 실행 중 생기는 untracked 산출물로 (f) 가 깨지지 않음 ✓ (스모크의 깨끗한 `run|git` 과 일치). 백그라운드 `ctl &` 의 stdin 은 /dev/null ✓. `ald.py` diff 4 hunk 는 dev·test 경로 문자 그대로 불변 ✓. 24 행 ROWS = §1a ✓ (1 라운드 D.1 그대로, 변경 없음).

MUST count = 0
