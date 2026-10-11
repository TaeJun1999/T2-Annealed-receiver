# 기록 감사 — NEXT_EXPERIMENTS_DMCBASE16e4.md §4 · §5 · §6 (DeepMIMO DMC baseline 확장, 태그 PILDMC / ALDDMC / SPDMC)

- 감사자: Claude Code (Fable 5.1 서브에이전트, 독립 기록 감사). 감사 시작 = 커밋 3e91b94b (10-10 22:53:20 CDT = 10-11 12:53:20 KST) 직후, 끝 10-10 23:07 CDT (`date` 로 읽음; 23:07:16 CDT = 13:07:16 KST).
- 감사 대상 판: 기록 파일 mtime 10-11 12:51:31 KST (= 10-10 22:51:31 CDT) = 커밋 **3e91b94b** 의 것 (감사 중 부모 세션이 §6 를 그대로 커밋함; 그 뒤 HEAD 89cde8a8 은 무관한 스크립트 추가, 기록 파일 diff 없음). 동결 §1~§2 (1~33 행) 는 501e0635 → HEAD 에서 **바뀐 글자 없음** (`git show 501e0635:… | diff`).
- 작업 트리 주의: 감사 중 13:10:17 KST (= 23:10 CDT) 에 부모 세션이 `conf/code` 11 파일 (`common.py`·`analysis.py`·`dmimo.py` 등; 새 prior `SRT` 추가) 을 수정했다 — 감사자의 변경이 아니다. 감사자의 두 실행 (`rerun_pairB_SPDMC.txt` 13:03:30 KST, `recompute_dmcbase.out` 13:05:11 KST) 은 그 전에 끝나 HEAD 의 코드로 돌았고, 그 실행이 import 하는 `sparse_tune.py`·`pair_baselines.py`·`recovery_ci.py`·`Demo` 는 수정되지 않았다.
- 방식: 읽기 전용. 새 파일은 이 폴더에만: `recompute_dmcbase.py` → `recompute_dmcbase.out` (numpy 로 네 raw 의 청크 직접 읽기; `pair_baselines.py` 미import, `pairB_SPDMC.txt` 미열람 — 기대값은 기록 §6 에서 손으로 옮김; 부트스트랩은 `recovery_ci.boot` 의 정의대로 재구현), `rerun_pairB_SPDMC.txt` (등록 도구 `pair_baselines` 를 `run_dmc_base.sh` 마지막 블록의 인자 그대로 재실행, 커밋본과 diff). GPU 미사용 (`CUDA_VISIBLE_DEVICES=`), CPU 2 스레드. git 상태·기존 파일 변경 없음. DMC16e4 (주 실행) 자체는 다시 감사하지 않았다 (`audit_DMC16e4.md`).

## 1. 재계산한 것과 재현 여부

| 항목 | 방법 | 검사 값 수 | 결과 |
|---|---|---|---|
| raw 청크 계획 {(40k, 40): k = 0..63} × 7 SNR — `raw_DMCB16e4`·`raw_PILDMC`·`raw_ALDDMC`·`raw_SPDMC` | 파일명 파싱 | 4 × 7 | **재현** (구멍·중복 없음; `\|failed` 키 없음; 비유한 blk_err 없음; 키 완전) |
| `run\|git` 448 청크 동일·"+dirty" 없음: base 27737b62 · PIL 3ddb0831 · SP 5aa7b9b4 · ALD ff736ea2 | 전 청크 | 12 | **재현** (= §6 "편차 2" 의 머리말 `base=27737b62 extra0=5aa7b9b4 pil=3ddb0831 ald=ff736ea2`) |
| raw meta: `ntrain` 160000, `bstar` kron, `kron_K` 4096, `ll_val\|kron` 122.37953759128766 (\|Δ\| ≤ 1e-9), `stagec_ckpt_id` (PIL·ALD·base) = sha 65b26ddd4f6437f4 epoch 812 role best; SP 는 `stagec_ckpt_id` 없음·"not requested"; arm 집합 3 / 3 / 4 / 14; ALD raw 의 `meta\|ald_file` = 경로 + sha ddee100645e9d8ab | 전 청크 | 27 | **재현** |
| **R5-genie 비트 동일**: 세 raw 각각 vs `raw_DMCB16e4`, 8 키 (blk_err·ber·nmse·tauL_gmean·alphaD·tauL_clip_frac·alphaD_clip·guardH) × 7 SNR × 2560 | `array_equal(equal_nan)` | 3 | **재현** (셋 모두 True) |
| pilot-only @1 == loop @1: `V1-pilot@1 == V1@1`, `bstar-pilot@1 == b*@1` (7 SNR) | 직접 | 2 | **재현** |
| `meta\|sparse` 448 청크 = 그 SNR 의 pick (`rho_sbl`·`rho_omp`·`n_em`·`L`) | 전 청크 | 1 (불일치 0) | **재현** |
| pick 이 `sparse_tune.per_snr_pick(tune_DMC_C2.json)` 으로 재현 (ρ·끝값 플래그·SNR 별 n_em/L/끝값); tune JSON prior DMC·cell C2·n 256·v2b 격자 | `sparse_tune` import (허용) | 3 | **재현** |
| §5 SPARSE 고른 값: ρ_SBL 8 (끝값 아님, 점수 −15.408) · ρ_OMP 16 (끝값 true, −14.202), n_em 3/5/5/5/5/5/5, L 2/2/3/4/6/8/12, SNR 별 끝값 없음, 개발 NMSE 14 값 (소수 2 자리) | pick JSON | 39 | **재현** |
| sha256[:16]: ckpt 65b26ddd4f6437f4 · pick ff25622dfcb0c7d5 · tune a16ae2aad0db242d · `tune_PILDMC.json` 8c92ea491d654012 · `tune_PILDMC_curves.npz` 5a8c367b695c979f · `ald_PILDMC.npz` ddee100645e9d8ab · `code/ald.py` 5d38e28679cc7542 (= tune 기록의 `ald_py_sha`, 즉 조정 뒤 `ald.py` 불변) | `sha256` | 7 | **재현** |
| §5 ALD 조정: c 0.01 · β 0.005, 멈춤 384/453/504/598/600/600/600 (≤ L·M 600), v 7 값 (4 자리), 개발 NMSE 7 값, 개발 최적 `c=0.01,beta=0.0001` −16.180, β = 0.005 의 최적 c −16.171 (차 0.0094 ≤ 0.1 dB → 기본값 유지 규칙 성립), 확장 [β 0.0001, 1e-05]·확장 뒤 끝값 없음, n_dev 512 · dev_skip 2560, ckpt_sha·ald_py_sha·git 48803fe6, `ckpt` 상대 경로 원문 = 스크립트가 넘기는 문자열 | tune JSON | 14 | **재현** |
| ALD 추정 파일 (`ald_PILDMC.npz`): `tune` JSON == `tune_PILDMC.json` 전체, `ckpt_sha`, `prov` (ckpt_sha·ald_py_sha·git ff736ea2 = 시작 3), v 배열 == tune v (비트), snrs·skip 0, hhat (7, 2560, 32); raw ALDDMC 의 `meta\|ald_tune` == tune JSON; ALD-pilot·ALDv-pilot 의 nmse 가 16 반복에서 고정 (14) | npz 직접 | 24 | **재현** (추가: raw ALD-pilot nmse@1 의 시행 평균 = 추정 파일 `nmse` 와 6 유효숫자 일치 — 정의가 같다는 보증은 없어 세지 않음) |
| 시험 ALD NMSE dB (추정 파일 평균) −8.07 / −10.94 / −13.41 / −16.22 / −18.99 / −21.26 / −23.92 (§6.3) | `10 log10` | 7 | **재현** |
| **BLER@16 실패 수 / 2560 표 22 행 × 7 SNR** (§6.2 의 11 곡선 + "11 곡선에 없는 등록 arm" 7 + R0-pilot@16·V0·V4·V4b) + genie −3 dB 0.686 | numpy 직접 | 155 | **재현** |
| **표 B 16 쌍 `X → V1`**: 판정점 (앵커 X 규칙 재적용; R3-bigamp 만 +6/+9/+12), a:b × 3, pooled a:b, pooled p (`%.2g` 문자열, 0 포함), POWERED, (V1 유의 k, X 유의 k), 라벨, F_X − F_V1(−3 dB), R_X(−3 dB) 점추정 + 90 % CI 또는 정의 안 됨 + BLER 4 자리, R_X(판정점 합) + CI; V1-pilot 의 SNR 별 p 0.25 · 0.043 · 0.29 | `math.comb` 정확 검정; 부트스트랩 `default_rng(20260926)` B 2000, 5/95 백분위 재구현 | 161 | **재현** (16 라벨 전부, CI 32 개 소수 3 자리까지) |
| 요약 줄: SUMMARY-B (i) 14 · (ii) 0 · 미판정 1; 16 개 (i) 15 · (ii) 0 · 1; (i) 아닌 집합 = {V1-pilot: (iii)}; X\* = M-ours-bstar F 2232, R_X\* 0.202 [0.166, 0.240]; "멀어진다" 조건 NOT met; "전부" 조건 불충족; SNR@0.1 16 쌍 + V1 모두 "> 15" → n/a | 직접 | 8 | **재현** |
| §6.1 끝 글머리 "0.9 를 넘는 **10 개**에서 정의되지 않는다" | 직접 | 1 | **불일치 → M1** (정의 안 되는 X 는 **11 개**) |
| §6.3 보고 전용 쌍 9 개 (`pair_cross`·`pair_ald` 형식; 앵커 = 첫 arm): 판정점·a:b·pooled·라벨·유의 점 수 | 직접 | 36 | **재현** |
| §2 예측 1~4 채점 (6.4) + §5 의 2 앞 문장 | 직접 | 7 | **재현** (1 적중 · 2a 적중 · 2b 적중 · 3a 적중 · 3b 적중 · 4 미발동) |
| 그림 기록 `paper_f21dmc.txt`: 11 행 실패 수 × 7 + raw 출처 11; "그려진 baseline 9 개 모두 (i)"; "제안 곡선 이하인 그려진 곡선 없음" | 기록 파싱 + 재계산 | 26 | **재현** — 단 "곡선 없음" 은 스크립트가 Perfect CSI 를 제외한 집합에 대한 문장 (→ S2) |
| 등록 도구 재실행 `pair_baselines … --provenance manifest` → `rerun_pairB_SPDMC.txt` | 커밋본 (첫 머리말 줄 제외) 과 `diff` | 1 파일 | **바이트 동일** |
| 시각 (KST → CDT): v1 커밋 18:39:47 · 동결 19:02:24 · ALD 개발 재생성 로그 19:17:59 → tune 19:26:40 · ckpt best 19:14:48 · sparse pick 21:28:44 · §5 커밋 21:55:07 · PIL 청크 21:55:40~21:57:28 · accept 21:57:43 · pair_PILDMC 21:57:48 · 시험 사이트 21:57:51 · 5aa7b9b4 22:22:51 · SP 청크 22:23:37~22:28:31 · accept 22:28:46 · 미리보기 png 22:31:41 · ff736ea2 22:31:17 · ALD 추정 22:47:06 · ALD 청크 22:47:16~22:47:32 · accept 22:47:46 · pair_ALDDMC 22:47:52 · pairB 22:48:02 · 그림 22:49:21 · genie_rank 22:50:18/27 · 기록 22:51:31 · 3e91b94b 22:53:20 | `date -r`, `git log` | 25 | **재현** (§4·§6 의 분 단위 시각 전부 일치; 1 건 자기 불일치 → N2) |
| 편차 기록 vs 사실: 세 번 시작 (21:55 · 22:22 · 22:46), 1 회 ABORT (등록된 동작), `DEFER_ALD=1` 은 시작 2 만, `git diff 3ddb0831 ff736ea2 -- conf/code Demo` = `run_dmc_base.sh` +10 −2 (스위치 꺼짐 = 기존 경로와 동일; 켜져도 빈 GPU 가 있으면 무효), 단계 간 커밋 2 회가 runner 비가동 중 (청크 mtime 과 교차), 각 raw 한 커밋, `DECISIONS.md` 12:22 KST 줄 존재·내용 일치, 사용자 인용 두 문장 = DECISIONS 361·363 줄 | 로그·git·mtime | — | **재현** |

합계: 자동 비교 **521 값 중 1 불일치** (M1), 도구 재실행 1 파일 바이트 동일, 수동 대조 시각 25 + 문구 — 자기 불일치 1 (N2).

**단계 순서 편차가 수치를 바꿀 수 있었는가 — 없다.** 네 raw 는 같은 시행 스트림 (`default_rng([20260926, TBID, PID, Nr, T, Tp, snr+100])`, skip 0..2520) 으로 각자 생성되고 (R5-genie 비트 동일이 그 증거), PIL·ALD·SP runner 는 서로의 출력을 읽지 않는다 (PIL: ckpt + fits 링크; ALD: ckpt·`tune_PILDMC.json`·시험 사이트; SP: pick JSON). 단계 사이에 들어간 커밋 (5aa7b9b4·ff736ea2) 의 `conf/code`·`Demo` 변경은 `run_dmc_base.sh` 만이고, 세 manifest 의 `code_hashes` (runner·arms·score·common·d2·analysis·rt_tap·p3_rules·dmimo·dmimo_build·Demo 3 파일) 는 셋 모두 동일하다. `pair_baselines --provenance manifest` 는 `run|git` 이 있는 raw 에는 manifest 검사를 적용하지 않고 "한 깨끗한 커밋" 규칙을 적용한다 (§1 의 설명대로) — 그래서 ALDDMC manifest 가 22:48 CDT 시점에 아직 미커밋이었어도 "integrity: OK" 는 올바른 출력이다.

## 2. 발견

### MUST-FIX

**M1 · §6.1 100 행 "R_X(−3 dB) 는 X 의 −3 dB BLER 이 0.9 를 넘는 10 개에서 정의되지 않는다(포화 가드)" — 11 개다.**
- 파일: `pairB_SPDMC.txt` 와 재계산 모두 "undefined (out of range)" 가 **11** 개: R0-pilot@1 (0.9871) · R1-turbo (0.9574) · R2-ours-G (0.9102) · R3-bigamp (0.9613) · R4-llr (0.9855) · R4-scvamp (0.9676) · bstar-pilot (0.9074) · ALD-pilot (0.9105) · ALDv-pilot (0.9160) · SBL-pilot (0.9199) · OMP-pilot (0.9035). 정의되는 것 5 개: b\* 0.202 · b\*-scalar 0.229 · gmm32 0.261 · V1-pilot 0.240 · SBL-loop 0.264. §6.1 의 표 자체도 "정의 안 됨" 을 11 행에 적고 있어 표와 글머리가 서로 어긋난다. (확신: 확실.)
- 교체 제안: `R_X(−3 dB) 는 X 의 −3 dB BLER 이 0.9 를 넘는 **11 개**(R0-pilot@1 · R1-turbo · R2-ours-G · R3-bigamp · R4-llr · R4-scvamp · bstar-pilot · ALD-pilot · ALDv-pilot · SBL-pilot · OMP-pilot)에서 정의되지 않는다(포화 가드); 정의되는 5 개 = b\* · b\*-scalar · gmm32 · V1-pilot · SBL-loop.`

### SHOULD-FIX

**S1 · §6.3 128 행 "등록 외 진단 … `DMCB16e4_genie_rank.txt`" — 주 실행(DMCB16e4)의 사후 분할인데 주 실행의 기록에는 없다.**
- 파일: `grep genie_rank` → `NEXT_EXPERIMENTS_DMC16e4.md`·`DECISIONS.md`·`WORK_QUEUE.md`·`docs/EXPERIMENTS.md` 모두 0 건; 이 DMCBASE 기록 §6.3 과 출력 파일 머리말에만 있다. 출력 파일 머리말 ("UNREGISTERED diagnostic, REPORT-ONLY … post-hoc split, asked by the user after the result was seen; written 2026-10-10 22:50 CDT, git ff736ea2") 자체는 적절하다. 다만 (a) DMC16e4 §6 ("추가만 한다") 에 같은 공개가 없어 주 실행의 기록만 읽는 독자는 사후 분할이 있었음을 모르고, (b) 스크립트가 감사자 폴더 `prereg_audit_2026-10-10/genie_rank.py` 에 들어가 있어 (mtime 22:50:18 CDT, 커밋 3e91b94b) 감사 산출물로 오독될 수 있다 — `audit_DMC16e4.md` 는 이 스크립트를 쓰지 않았다. (확신: 미공개 사실은 확실; 심각도는 중간 — 수치·라벨과 무관.)
- 교체 제안: ① `NEXT_EXPERIMENTS_DMC16e4.md` §6 끝에 추가: `- **등록 외 진단(보고 전용 — 라벨·검정·CI 없음; 결과를 본 뒤 사용자 질문으로 한 사후 분할, 10-10 22:50 CDT, git ff736ea2)**: `results/review_next/DMCB16e4_genie_rank.txt` — 시행을 채널 최대 특이값의 에너지 비중으로 나눈 Perfect CSI · V1 · b\* 의 BLER@16. 스크립트 `results/review_next/prereg_audit_2026-10-10/genie_rank.py` (감사 산출물이 아님; 부모 세션 작성).` ② 이 기록 128 행 끝에 `(주 실행의 진단; 같은 공개를 DMC16e4 §6 에 둔다)` 를 붙인다. ③ 스크립트 위치는 사용자 결정 (예: `code/` 로 옮기고 머리말에 "report-only, unregistered" 명시) — 감사자는 파일을 옮기지 않는다.

**S2 · §6.2 120 행 "제안 곡선 이하인 그려진 곡선 없음(점추정)" 과 그림 기록 `paper_f21dmc.txt` "Drawn curves at or below the proposed curve … : none" — Perfect CSI 는 그려진 곡선이고 7 SNR 모두 제안 곡선 아래다 (1756 < 2136 … 611 < 801).**
- 파일: `paper_f21dmc.py` 77~78 행 `below = [... for a in SHOW if a not in (V1, GE) and (cur[a] <= cur[V1]).any()]` — 집합은 "그려진 **baseline** 9 개" 이고 Perfect CSI 는 제외된다. 재계산: baseline 9 개 가운데 어느 SNR 에서도 제안 곡선 이하인 것 없음 (True); Perfect CSI 는 전 SNR 아래 (True). 문장이 글자 그대로는 거짓이고, 뜻은 맞다. (확신: 확실; 심각도 낮음 — 문구.)
- 교체 제안 (기록 120 행): `제안 곡선 이하인 그려진 **baseline** 곡선 없음(Perfect CSI 제외; 점추정)`. 그림 기록은 스크립트가 생성하므로 (`paper_f21dmc.py` 89 행 문자열) `"Drawn baseline curves (Perfect CSI excluded) at or below the proposed curve …"` 로 바꾸고 다시 돌릴지는 사용자 결정 — 그림·수치는 바뀌지 않는다; 감사자는 스크립트를 다시 돌리지 않았다.

### NIT

**N1 · §6.1 98 행 "… R_X\*(−3 dB) = 0.202 [0.166, 0.240] 이나 k = 16 이 (i) 가 아님"** — "k = 16 이 (i) 가 아님" 은 뜻이 서지 않는다 (조건은 k = (i) 의 수 = 16). 교체: `… 이나 (i) 가 16 개 중 15 개 (k = 15 ≠ 16) 라 조건 불충족`.

**N2 · §4 43 행 "§5 채움(10-10 21:54 CDT)" vs §5 49 행 "갱신 2026-10-10 21:53 CDT"** — 같은 커밋 (3ddb0831, 21:55:07 CDT) 안의 1 분 자기 불일치. 교체 (43 행): `§5 채움(10-10 21:53 CDT; 커밋 3ddb0831 21:55 CDT)`.

**N3 · §6 70 행 (시작 3)** — ALD 시험 사이트 파일 `results/ald/pilots_PILDMC_test.npz` 는 시작 1 (git 3ddb0831, 21:57:51 CDT) 에서 만든 것을 스크립트 규칙 (`[ -f … ] ||`) 대로 재사용했다. `ald.py` sha (5d38e28679cc7542) 와 `dmimo.py` 해시 (manifest 셋 동일) 가 불변이라 수치 영향은 없다. 추가 제안: `… ALD 추정 GPU 0 (22:47 CDT; 시험 사이트 파일은 시작 1 의 것 21:57 CDT 재사용) …`.

**N4 · §6 70 행 "GPU 0·1·2 가 빈 것을 `nvidia-smi` 로 확인한 뒤, 스위치 없이"** — 로그로 확인되지 않는다 (빈 GPU 가 있으면 `DEFER_ALD` 가 켜져 있어도 "ALD deferred" 줄이 나오지 않으므로 로그는 두 경우를 구분하지 못한다). 틀렸다는 뜻이 아니라 검증 불가. 원하면 `(로그 외 사실)` 를 붙인다.

**N5 · `docs/EXPERIMENTS.md` 에 DMCBASE16e4 (PILDMC·ALDDMC·SPDMC) 행이 없다** — 프로젝트 규칙 "실험이 끝나면 즉시 한 행". §6 는 커밋됐으니 (3e91b94b) 행을 추가할 때다: 날짜 10-10 CDT, 설정 §5 인자 원문, seed 20260926, 커밋 3ddb0831/5aa7b9b4/ff736ea2 (raw 별), GPU 0 (ALD 추정만), 핵심 지표 "(i) 15 / 16, V1-pilot (iii)", 로그 `logs/run_dmc_base.log`.

**N6 · §6 62 행 머리말** — 전사의 커밋 해시가 없다 (쓸 때는 없었다). 이제 있으므로 `(기록 2026-10-10 22:51 CDT … ; 커밋 3e91b94b 22:53 CDT)` 로 보완하면 §5 (3ddb0831) 와 대칭이 된다.

**N7 · §6.1 97 행 "'비긴다'·'동등' 이 아니다"** — 부정문이지만 §1 의 금지 문구가 글자로 들어가 grep 에 걸린다. 교체: `§1 이 금지한 동치 문구는 쓰지 않는다`. (아주 사소.)

## 3. 규칙 재적용 · 예측 채점 · 편차 공개 (판정)

- **"전부" 문장**: §1 조건 = `b* → V1` (i) **이고** 15 개 모두 (i). 재계산 b\* (i), 15 개 중 (i) 14 · V1-pilot (iii) → 조건 불충족 → **보류가 맞다**. 대체 문구 규칙 ("(i) 의 수와 (i) 가 아닌 arm 의 이름·라벨을 그대로 적고 '전부' 를 쓰지 않는다") 대로 97 행에 "(i) 14 / 15 (b\* 포함 15 / 16), (ii) 0; V1-pilot (iii)" 을 적었다 ✓. "비긴다"·"동등" 을 만들지 않았다 ✓ (N7 은 문구 위생).
- **"멀어진다" 문장**: "전부" 조건 위에 R_X\*(−3 dB) CI 하한 > 0 — X\* = M-ours-bstar (F 2232, 16 개 중 최소; 동률 없음), 0.202 [0.166, 0.240] 로 하한은 > 0 이지만 k = 15 ≠ 16 → NOT met → **보류가 맞다** ✓.
- **드리프트 검사**: `pair_baselines` 의 `b* → V1` (127:46 · 111:42 · 119:36, pooled 357:124 p 3.4e-27, (i), R 0.202 [0.166, 0.240], 판정점 합 0.279 [0.241, 0.316]) = DMC16e4 §6.1 144·151 행 → 드리프트 없음 ✓ (재계산도 같음).
- **필수 부속 문구**: 101 행에 DMC16e4 §1 "DMC 고유 사항" (1)(2)(3) (유한 풀 52,172 쌍 · 누수 0.433 · outage genie −3 dB 0.686) 과 "DMC 고유 1" (조정용 개발 채널이 테스트 풀에서; baseline 에 유리) 과 범위 한정 ✓. (누수 0.433 은 DMC16e4 의 값이라 여기서 재계산하지 않음; genie 0.686 = 1756/2560 ✓.)
- **순서·열람 규칙**: 동결 19:02:24 CDT < `tune_PILDMC.json` 19:26:40 < 주 실행 BLER 시작 20:04 < pick 21:28:44 < §5 21:53~21:55 < 실행 21:55 — §4 42 행 "동결 시점 관측 상태" 와 §5 59 행 "동결 뒤·실행 전 관측 공개" 가 파일 시각과 일치 ✓. §2 2 의 L 문장은 pick 을 읽기 전 (동결) 에 적혔으므로 예측으로 채점한 것이 맞다 ✓.
- **예측 채점 (6.4)**: 1 적중 ((ii) 0, (i) 14 ≥ 13; 후보 둘 중 V1-pilot 만 (iii)) ✓ · 2 앞 (L 2, 2 ≤ 4) 적중 ✓ (§5 와 동일) · 2 뒤 (OMP 2313 < 2527, 2039 < 2413; SBL-pilot 2355 < 2527, 2021 < 2413) 적중 ✓ · 3 (2331 > 2256, 1910 > 1837, 1610 > 1559; A3 (i)) 적중 ✓ · 4 미발동 ✓.
- **편차 공개**: 로그·git·DECISIONS·diff·mtime 과 대조해 §6 "실행·운영 기록" 다섯 글머리 모두 사실과 일치; 공개되지 않은 사건은 찾지 못했다 (단 N3 의 시험 사이트 재사용은 공개가 덜 됐고, S1 의 사후 분할은 다른 기록에 공개가 없다). "미리보기 그림" (편차 3) 은 세션 scratchpad 의 `preview/DMC_preview_10curves.png` (mtime 22:31:41 CDT, SP 종료 22:28 ~ 시작 3 22:46 사이) 로 뒷받침된다. §6 에 해석 문장 없음, 손으로 적은 근사 시각 ("약", "쯤", 자리표시자) 없음 ✓.
- **그림 기록**: 11 행 실패 수·raw 출처 모두 재계산과 일치; 그려진 baseline 9 개 라벨 모두 (i) ✓; "곡선 없음" 문장은 S2.

## 4. 검증하지 못한 것

- 10-10 21:55 CDT 직전 GPU 6 장을 컨테이너 밖 프로세스가 점유 (장당 39,689 MiB, Exclusive_Process) 했다는 것, GPU 5 에 CUDA 컨텍스트를 한 번 열어 `cudaErrorDevicesUnavailable` 을 받았다는 것, 시작 3 전 GPU 0·1·2 가 비었음을 `nvidia-smi` 로 확인했다는 것 — 로그 산출물이 없고 (DECISIONS·기록의 서술만), 감사 제약 (GPU 접근 금지) 상 `nvidia-smi` 도 돌리지 않았다. 로그의 `ABORT: no free GPU` (21:57) 와 `ALD estimate on GPU 0 done` (22:47) 은 서술과 모순되지 않는다.
- 사용자 인용 두 문장 ("GPU 다 우리거니까 지금은, 계속 진행해", "그러네. GPU 안쓰는거 먼저 해보자") — DECISIONS 361·363 줄과 글자 일치만 확인.
- §4 의 "갱신 10-10 22:22 CDT" · "22:30 CDT" 같은 자기 시각 — `date` 로 읽었다는 서술만 (파일 mtime 은 마지막 저장 22:51:31 CDT 하나).
- 누수 0.433 · "DMC 고유 사항" (1)(2)(3) 의 수치 — DMC16e4 감사 범위 (재감사 안 함).
- ALD 추정의 GPU float32 결정성 (`ald.py` 가 같은 시드로 재계산해 `array_equal` 을 assert 하는 것은 코드로 확인; 실행 자체는 재현하지 않음 — GPU 금지).
