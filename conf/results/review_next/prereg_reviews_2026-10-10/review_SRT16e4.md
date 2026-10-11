# 적대적 검토 — NEXT_EXPERIMENTS_SRT16e4.md v1 (Sionna RT 2.1, prior SRT, 태그 SRTB16e4 / PILSRT / ALDSRT / SPSRT) + `code/srt_build.py`·`run_srt_*.sh`

- 검토: Fable 5.1 서브에이전트, 2026-10-10 23:34 → 23:50 CDT (= 10-11 13:34 → 13:50 KST). 대상 = 커밋 c9b09731 의 초안 v1 (131 행), 틀 문서 `NEXT_EXPERIMENTS_DMC16e4.md` v2 §1~§2 · `NEXT_EXPERIMENTS_DMCBASE16e4.md` v2 §1, 코드 d1fd0227/f379258f 의 `srt_build.py`·`dmimo.py`·`run_srt_*.sh`·`rank_strata.py`, Sionna RT 2.1 소스(`sionna/rt/path_solvers/paths.py`, `scene.py`, `utils/geometry.py`, `constants.py`; 읽기만, import 안 함).
- 읽기 전용; 새 파일은 이 디렉터리의 `srt_pool_check.py`(풀 재계산, CPU 5 s) → `srt_pool_check.out` 만. BLER 코드·GPU·레이 트레이서 미실행. **SRT 의 ll_val·b\*·조정 점수·GB′ 는 읽지 않았고 이 보고에도 없다**(파일 존재 여부·개수만).
- 분류: MUST = 등록/스크립트가 틀렸거나 실행 불가거나 라벨을 바꿀 수 있는 결정이 열려 있음; SHOULD = 모호·공개 누락·추가할 검사; NIT = 문구.

## 발견 (심각한 순)

### M1 · MUST · GB′ 의 순서가 문서 안에서 서로 다르고, 스크립트는 "§5 전" 쪽으로 돈다 [읽어서 확인]
- §1 "순서 규칙"(67 행): "**GB′ 는 보고 전용**: 격자 확정 뒤 GPU 에서 계산하며 **주 실행과 겹쳐도 된다**(값은 §6; DMC16e4 는 §5 전에 계산했다 — 여기서는 … 바꾼다)"; §1 "수용 검사"(70 행) (e) 는 "§6 에서 확인".
- §4(122 행): "병합·b\* 선택 → ALD 개발 재생성·조정 **+ GB′ (`run_srt_post_gpu.sh`) → §5** → 주 실행". `code/run_srt_post_gpu.sh:2-3, 15-16` 머리말 "the two GPU steps that **precede §5**", lane A = GB′ 를 ALD 조정과 **함께** 돌린다(스위치 없음).
- 왜 중요한가: (a) 둘 중 어느 것이 등록인지 정해지지 않아 §5 를 쓸 때 GB′ 를 봤는지 아닌지(예측 6 의 "BLER 전 채점" 여부)가 작성자 선택이 된다. (b) 스크립트를 그대로 돌리면 §1 의 순서를 어긴 채 §4 의 순서가 실행된다. (c) (e) 를 §6 으로 미루면 (e) 가 어긋났을 때(GB′ 로그의 b\* ≠ §5 b\*) 무엇이 무효인지 적혀 있지 않다.
- 고칠 것(둘 중 하나로 통일; 추천 = §1 쪽, 대기 시간 절감이 이유라고 이미 적혀 있다):
  - §4 122 행: `병합·b\* 선택 → ALD 개발 재생성·조정 (run_srt_post_gpu.sh 의 lane B 만) → §5 → 주 실행 (+ GB′ 를 GPU 에서 겹쳐 계산, run_srt_post_gpu.sh 의 lane A) → 수용 → …`
  - `run_srt_post_gpu.sh`: lane 선택 인자 추가, 예: 4 번째 인자 `LANES=${4:-AB}`; `[[ $LANES == *A* ]] && ( … GB′ … ) &`, `[[ $LANES == *B* ]] && ( … ALD … ) &`; 머리말 "precede §5" → "lane B precedes §5; lane A (GB′) runs after the §5 commit, overlapping the main run (SRT16e4 §1)".
  - §1 70 행 (e) 뒤에 한 문장: `(e) 가 어긋나면 GB′ 만 무효(재계산 뒤 §6); 주 실행·라벨은 영향 없다. GB′ npz 의 mtime 은 격자 확정 시각보다 뒤여야 한다(§6 에 나란히).`
  - 이미 확인한 것: `score.train` 재개는 정지 규칙을 만족한 체크포인트를 **건드리지 않는다**(`score.py:847, 957`) → GB′ 가 §5 뒤에 돌아도 `ckpt/*.pt` sha(§5·`run_prior_eval.sh:23-24`·수용 (c))는 바뀌지 않는다. 겹쳐 돌려도 안전.

### M2 · MUST · `run_srt_base.sh` 는 b\* 가 kron 인 경우만 실행된다 — §3 14(e)(full 512 → full 1024) 가 발동하면 등록된 명령이 돌지 않는다 [읽어서 확인]
- `code/run_srt_base.sh:19` `BS=kron; KK=$5; LL=$6 … (this script assumes a kron b*)`, `:25` 6 인자, `:33` `fit_${PR}_Nr8_kronK${KK}` 의 ll_val 대조, `:39` `KARG="--kron-K $KK"`. §1 69 행은 `<kron_K> <ll_val>` 인터페이스를 등록하면서 kron 가정을 적지 않았고, §3 14(e)·§1 65 행은 full 끝 규칙을 등록했다.
- 고칠 것(최소): §1 69 행에 `(스크립트는 kron b\* 를 가정한다; b\* 가 full 계열이면 §5 커밋에서 bstar·K 인자를 run_prior_eval.sh 와 같은 꼴 <bstar> <kron_K|-> 로 고친다 — 동작 불변, BLER 전)`. 더 나은 것: 지금 7 인자 `<ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16> <bstar> <kron_K|-> <ll_val>` 로 바꾸고 `:33` 의 파일명을 `fam=$([ "$BS" = kron ] && echo kron || echo full); K=$([ "$KK" != - ] && echo $KK || echo ${BS#gmm})` 로.

### S1 · SHOULD · 사이트 채택 규칙에 공개되지 않은 선택이 하나 있다 — 섹터 고리의 실외 비율이 ~25 % 미만인 사이트는 통째로 버린다 [코드 확인 + 빌드 로그]
- `srt_build.py:143-148`: 4·NC 개를 뽑아 `on_ground` 로 거르고 `[:n_rx]`; **`len(xy) < n_rx` 이면 사이트를 건너뛴다**(주석 "fewer than NC outdoor points among 4 NC candidates: skip the site"). 머리말(16-19 행)과 §1 61 행 "사이트 'rs'" 는 "지상일 때만 채택" 만 적는다. 빌드 로그: munich 210 추첨 → 139 사이트, florence 282 → 145 — 탈락에는 BS 지상 판정 실패와 **이 규칙**이 섞여 있고 비율은 기록되지 않았다. 방향: 빽빽한 구역의 사이트가 덜 대표된다(모집단 가중 (4) 에 없는 항목).
- 고칠 것: §1 61 행 "사이트 'rs'" 와 `srt_build.py` 머리말 18 행에 `; 4·NC 균등 후보 가운데 실외가 NC 개 미만(실외 비율 < 25 %)이면 그 사이트는 버린다` 추가; §1 63 행 (4) 에 같은 문장.

### S2 · SHOULD · 지상 판정은 지붕 없는 폐쇄 구역(안마당·지붕 메시가 없는 건물)을 통과시킨다 — 로그에 그 흔적이 있다 [빌드 로그 확인]
- `logs/srt_build.log`: munich site 20 "with-path 0.000 (kept 1)", site 60 "0.001 (kept 7)", site 10 "0.030": 지상 판정을 통과한 BS 인데 8192 후보 가운데 거의 아무 UE 도 경로가 없다 → 10 m 높이의 BS 가 벽에 둘러싸인 자리(지붕 없는 폐쇄 구역)다. 쌍은 "경로가 하나라도 있는 후보" 규칙이 걸러내므로 풀에는 8 쌍만 들어갔다(수치 영향 없음). 그러나 §1 61 행 "지상(위에서 내려 본 표면이 1 m 아래)" 은 "건물 안이 아님" 과 같지 않다.
- 고칠 것: §1 61 행·머리말 17 행에 `(지붕이 있는 건물 안은 걸러지지만 지붕 없는 폐쇄 구역은 통과한다; 그런 사이트는 경로 있는 쌍이 거의 없어 쌍 규칙이 걸러낸다 — 빌드 로그 munich site 20·60)`.

### S3 · SHOULD · "split 이동" (5) 에 장면 비중이 빠져 있다 (DMC 검토 S3 와 같은 지적) [재계산]
- `srt_pool_check.out`: 장면별 테스트 비중 munich 0.1602 / etoile 0.1436 / florence 0.1463 → 테스트 풀의 장면 구성 **0.356 / 0.319 / 0.325**(학습 풀 ≈ 1/3 씩). §1 63 행 (5) 는 "테스트 타일은 다른 장소(§0 TDMg)" 만 적는다.
- 고칠 것: (5) 에 `; 장면 비중 학습 풀 ≈ 0.333 씩 → 테스트 풀 munich 0.356 / etoile 0.319 / florence 0.325 (911 타일 추첨의 결과; 고치지 않는다)`.

### S4 · SHOULD · 예측 12 (랭크 층화) 는 +15 dB 가 판정점일 때만 채점된다 — 조건을 적어야 한다 [코드 확인]
- `rank_strata.py:38` `snrs = sorted({-3.0, *decision_snrs(tag)})` → 출력은 −3 dB 와 판정점 3 개뿐. 예측 2 가 "판정점 = +9/+12/+15" 라고 따로 걸고 있지만 12 는 그에 조건부다. 또 "비중 < 0.80 인 두 층을 합쳐 ≤ 0.02" 의 계산식이 없다(스크립트는 층별 n·실패 수를 찍는다).
- 고칠 것(§3 12): `+15 dB 가 랭크 층화 SNR(−3 dB + 판정점) 에 없으면 채점 불가. "합쳐" = 두 층의 Perfect CSI 실패 수 합 / n 합 (SRTB16e4_rank_strata.txt 의 failures·n 열).` 참고: 테스트 풀에서 비중 < 0.60 층은 0.3 % (≈ 8 시행/점), 0.60–0.80 은 4.2 % — 합쳐 ≈ 115 시행.

### S5 · SHOULD · 접속 예측 2·10 에 채점 규칙이 없다; 3 의 "발동" 조건이 반쪽이다 [읽어서 추론]
- 예측 2 는 네 절(genie −3 ≥ 0.70, genie +15 ≥ 0.25, 판정점 = +9/+12/+15, 전 arm SNR@0.1 n/a) — 7 처럼 "모두 맞아야 적중" 인지 따로 채점인지 없다(DMC 감사 N2 가 같은 문제를 지적했다). 10 "유의 방향 없음(0/3 · 0/3)" — 라벨 (iii) 인지 정확히 0/3 · 0/3 인지(1/3 · 0/3 도 (iii) 다). 3 "포화 가드가 발동한다: b\* BLER@16 > 0.9" — 가드는 "b\* 실패 ≤ genie 실패" 로도 발동한다(§1 72 행).
- 고칠 것: 2 → `넷 다 맞아야 적중; 하나라도 n/a 가 아닌 SNR@0.1 이 있으면 넷째 절 빗나감`; 10 → `채점 = 라벨 (iii) (어느 쪽도 ≥ 2/3 아님)`; 3 → `BLER@16(−3 dB) > 0.9 로 발동하면 적중; 다른 조건으로만 발동하면 채점 불가; 미발동 = 빗나감`.

### S6 · SHOULD · 동결 전 열람 금지 목록이 DMCBASE16e4 보다 좁고, 동결 줄에 "그때 무엇이 있었나" 를 적는 규칙·병합 파일 mtime 규칙이 없다 [디스크 확인]
- 지금(23:47 CDT) 디스크: `results/gmm_fits_D2_SRTB16e4/` **3 파일**(kron 1024 후보; 13:36–13:4x KST), `logs/tb2_gpu{0,1,2}.log` 81/104/142 줄(적합 로그는 ll_val 을 찍는다), `logs/sparse_tune_SRT_C2.log` 0 줄, `results/sparse/{tune,pick}_SRT_C2.json` 없음, `logs/train_d2sx_SRT_N160000_a1.log` 158 줄(학습 곡선), GB′·ALD 파일 없음. §1 67 행은 "ll_val·GB′·pick·ALD 조정 점수를 읽지 않는다" 만 적고 **파일 이름**이 없다; DMC16e4 §4 "순서 규칙" 의 "병합 파일 mtime 이 동결 커밋보다 뒤" 조항도 빠졌다.
- 고칠 것(67 행): `읽지 않는 것: results/gmm_fits_D2_SRTB16e4/*, logs/tb2_gpu*.log 의 ll 줄, logs/sparse_tune_SRT_C2.log, results/sparse/{tune,pick}_SRT_C2.json, results/ald/tune_PILSRT.json, logs/ald_tune_PILSRT.log, results/d2_gbprime_SRT*. 동결 줄(DECISIONS.md)에 그 시각의 fit 파일 수·tune/pick 존재 여부·학습 epoch 을 적는다. 병합 파일 fit_SRT_Nr8_kronK{1024,2048,4096}_n160000.npz 와 GB′ npz 의 mtime 은 동결 커밋 시각보다 뒤여야 한다(§5·§6 에 나란히).` §3 머리말에 `동결 시각에 학습 epoch ≥ 300 이면 7 의 하한은 관측이다(채점은 patience·≤ 1200 만)`.

### S7 · SHOULD · `DEFER_ALD` 경로의 부분 결과 열람을 미리 공개할 것 [읽어서 추론]
- `run_srt_base.sh:59-65, 128`: ALD 보류 → SP 뒤 `SRT_BASE_PARTIAL` 종료 → 재실행. 그 사이 `raw_SPSRT`·`pair_PILSRT.txt` 의 BLER 을 볼 수 있다(DMCBASE §6 "편차 3" 이 실제로 그랬다). ALD 조정은 §5 의 `tune_PILSRT.json` sha 로 잠겨 있어 바꿀 수 있는 것은 없지만, 등록 문서가 "등록된 동작" 으로 삼은 이상 열람 가능성도 미리 적는 편이 낫다.
- 고칠 것(69 행): `DEFER_ALD 경로에서는 ALD 단계 전에 PIL·SP 의 raw 가 존재한다 — 읽었으면 §6 에 적는다; ALD 의 조정·명령은 §5 에 고정돼 있어 바꿀 것이 없다.` `run_srt_base.sh:59` 주석 "not the registered default" → "SRT16e4 §1 registers it as the no-free-GPU branch".

### S8 · SHOULD · NMSE CDF 는 "스크립트 없음" 이 아니다 — `conference/figures/paper_f33cdf.py` (커밋 331dba15, 10-10 23:35 CDT, 초안 커밋 1 분 뒤) 가 있고, 거기 고정된 규칙을 문서에도 적어야 한다 [파일 확인]
- 스크립트 머리말이 고정한 것: 4 패널 = −3 dB + 판정점 3(표에서 읽음), 곡선 = `paper_f16deep.SHOW` − Perfect CSI (10 개), NMSE = raw `nmse` 의 마지막 열(@16; R0-pilot@1 은 그 단일 열), x = 10 log10, XLIM (−35, 5) dB 는 그리기에서만 자름, **비유한·비양수 NMSE 는 +∞(오른끝) 로 세어 기록**, 2560 시행 전부, 중앙값·90 백분위. §1 73 행은 SNR·반복·곡선만 적는다.
- 고칠 것(73 행): `구현 conference/figures/paper_f33cdf.py @331dba15 (SRT 인자), F33cdf_SRT_wide; 비유한·비양수 NMSE 는 +∞ 로 센다(기록에 개수); x 범위 [−35, 5] dB 는 그리기에서만; 입력 raw = raw_SRTB16e4 / raw_ALDSRT / raw_SPSRT.` 74 행 "일반화해" → 이미 됐다: `paper_f21dmc.py:39, 108-109` 의 `SETS["SRT"]` → `F21srt`.

### S9 · SHOULD · 수용 (c) 의 배너 조건을 글자 그대로 적을 것 [실행 확인]
- `common.banner("D2", "SRT")` 에는 "sparse specular" 도 "CLAIM TESTBED" 도 없다(DM_WARNING 은 "NOT sparse specular" 를 담았었다 — DMC 감사 N4 의 원인). 검사 문자열을 못 박으면 기계 검사가 된다.
- 고칠 것(70 행): `(c) analysis 머리말에 문자열 "SITE-SPECIFIC RAY-TRACED TESTBED (prior SRT)" 가 있고 "CLAIM TESTBED -- sparse specular" 가 없다`.

### S10 · SHOULD · 검토 중에 생긴 미커밋 스크립트 `code/run_srt_post_select.sh` (mtime 13:36:38 KST) 가 문서에 없다 [파일 확인]
- 병합·b\* 선택·격자 끝 규칙·fit 파일 목록·`last` 링크 생성을 자동화한다(동결 커밋 해시를 받아 그 커밋의 문서 머리말에 "사전 등록 v2" 가 있는지, `tb2.log` 에 21 적합 `done rc=0` 이 있는지 검사; CPU; BLER 없음). 문서 §1 65 행·§4 122 행은 병합을 "DMC16e4 §1 과 같다(수동)" 로만 인용한다. 좋은 방향이지만 (a) 동결 커밋에 함께 넣고 §1 65 행에 `병합·선택 = code/run_srt_post_select.sh <동결 커밋> (logs/tb2_post_SRT.log)` 로 적을 것, (b) 27 행의 끝 규칙 판정이 22 행 print 의 **문자열 형식**(`SELECT b* = kron kron_K = 2048 `)에 묶여 있다 — 형식을 바꾸면 4096 병합이 조용히 건너뛰어진다; `sel` 이 `b kK` 를 파일(예: `$L.sel`)에 쓰고 그것을 읽는 편이 안전하다, (c) 13 행 `n` 은 병합 전 개수를 세는데 15 행 로그에만 쓰인다 — 그대로 두되 §5 의 "파일 24 개" 는 32-39 행 목록에서 센다고 적을 것.

### N1 · NIT · 랭크 비중 수치의 모집단이 모호하다 [재계산]
- §0 45 행 "SRT 학습 풀 0.816 / 테스트 풀 0.794 (0.80–0.95: 0.160, < 0.80: 0.046)". 풀 파일로 다시 재면 fit 풀 **0.815** / val 0.816 / 테스트 풀 **0.796** (0.159 / 0.045; 중앙값 0.9997). 0.794·0.816 은 학습 집합(스트림 7, 160000)과 테스트 스트림 추첨에서 잰 값으로 보인다. 어느 쪽인지 적을 것: `(학습 스트림 7 의 160000 표본 / 테스트 풀 51,852 쌍 전체 또는 스트림 10 추첨 n = …)`.

### N2 · NIT · san_francisco 탐침(2413 추첨 중 3 곳)은 산출물이 없다 [grep]
- `logs/`·`results/` 에 흔적 없음. §0 9 행에 `(로그 외 사실; 스크래치 탐침, 산출물 없음)` 표시.

### N3 · NIT · 수치 출처·반올림 [확인]
- §0 27 행 "최대 특이값 에너지 비중 ≥ 0.95 인 시행(전체의 0.67)" 과 45 행 "DeepMIMO … 테스트 0.657" — 전자는 `DMCB16e4_genie_rank.txt` 의 **시행** 비율, 후자는 풀 비율. 27 행에 출처 파일을 붙이고 소수 세 자리로.
- §1 63 행 (1) 에 DMC 처럼 기대 중복을 적을 것: `2560²/(2·51,852) ≈ 63 쌍`.
- §1 61 행 "장치 boresight 에 수직인 수평 ULA" — Sionna PlanarArray 1×N 은 로컬 y 축 ULA(소자 오프셋 `PlanarArray.positions`), 방향 [yaw, 0, 0] = z 축 회전 `rotation_matrix` (`utils/geometry.py:89-124`) — 맞다; 머리말 67-70 행의 시드 배치 `[SEED, TBID['D2'], 12, PID['SRT'], scene_index]` / 병합 `[…, 3]` 를 §1 62 행에 적을 것(DMC16e4 는 적었다).

### N4 · NIT · `dmc_leak_strata.py:58-59` 출력 머리말 "REPORT-ONLY (NEXT_EXPERIMENTS_DMC16e4 §1)" — SRT 실행에서도 DMC 문서를 가리킨다. `--prior SRT` 일 때 `SRT16e4 §1` 로 바꾸거나 "DMC16e4 §1 의 정의(SRT16e4 §1 이 인용)" 로.

### N5 · NIT · 금지 문구 grep [grep]
- 91 행 '"ray-traced 채널에서"·"실측 채널에서" 같은 한정 없는 주장을 쓰지 않는다' — DMCBASE 감사 N7 과 같은 유형(부정문 안의 금지 문구). `§1 이 금지한 한정 없는 주장을 쓰지 않는다` 로.

### N6 · NIT · §1 61 행 "소자 오프셋 차 ≤ 1.4e-9 m, 채널 상대 오차 ≤ 3.7e-07" 는 `srt_build.py selfcheck munich` 의 콘솔 출력인데 파일로 남아 있지 않다. 재실행 가능하지만(GPU) 지금은 "로그 외 사실" 표시가 맞다. 또 cfr 의 위상 2π·fc·τ (≈ 1.2e5 rad, float32) 분해능 ≈ 8e-3 rad — 결정성에는 영향 없음(selfcheck 3.7e-7), 통계에도 무해; 한 구절로 적어 두면 뒤에 "왜 재생성 sha 가 다른가" 질문을 막는다.

## 확인한 것 (직접 확인한 것만)

**실행으로 확인 (CPU, 읽기 전용)**
- 풀 재계산 `srt_pool_check.out`: sha H.npy `b9f47f1c7c10a014` / split.npy `bd7019926eb03e6f` = `dmimo.POOL_SHA`; part sha 3 개 = §0; 345,600 = fit 273,748 + val 20,000 + test 51,852 (0.1500); 타일 5,982 / 테스트 911 / 양쪽 타일 0; (장면, 타일) 삼중쌍 수 = 키 수(키 충돌 없음); 장면당 115,200, 쌍 낸 사이트 139/124/139, 사이트당 최대 1000; LoS 0.8477 (학습쪽 0.8476 / 테스트쪽 0.8482), 평균 경로 2.953; **P_RAW 1.027118787916483 (차 0), TRAIN_SHA d15b033bc915cf88**; 스트림 7 = 서로 다른 160000 쌍, 전부 fit 풀; TDMa 0.99564 (s.e. 0.00249, CV 0.354); 테스트 스트림 0.9917; TDMh 중앙값 0.0500 / < 0.1 비율 0.634 — §0 표와 모두 일치. 원 풀의 쌍별 ‖H‖²/(NrNt): 중앙값 1.0000, 평균 1.026, 최소 0.0022, 최대 8.10(다중경로 간섭).
- 드라이런: `analysis.PAT` 가 `D2_C2_SRT_Nr8_T16_Tp4_eig_snr-3_skip0_n40.npz` 를 prior `SRT` 로 파싱; `common.banner("D2","SRT")` 에 "prior SRT" 있음·"sparse specular"/"CLAIM TESTBED" 없음(D2 배너에는 "CLAIM TESTBED -- sparse specular" 있음); `C.make_gen("D2","SRT",8,4)` → `DMGen`; 스트림 7·8·10, C2 7 SNR 시행 스트림, C1 시행 스트림, `sparse_tune` 개발 스트림 모두 추출됨; 스트림 9·DMC 스트림 7·DMC sparse 스트림은 ValueError; `C.DEV_SKIP0 = 2560`(ALD 개발 = 시행 스트림 → 테스트 풀); `make_pilots("D2","SRT",4,4,8)` 반환(eigen); `score._rung_ix("D2SXSRT160000") = 1753` — 기존 rung 8 개와 충돌 없음; `sigma.CHAT_FROM_TRAIN` 에 SRT; `runner` import OK. `python code/dmimo.py selfcheck 8 SRT` → OK (train sha 동일). `bash -n` 8 스크립트 OK.
- 디스크·시각: `srt_build.py` mtime 13:06:50 KST (빌드 시작 13:07 KST, 커밋 d1fd0227 13:18:10 KST) → 세 장면 프로세스와 병합이 **같은 파일**로 돌았다(§0 29 행의 주장 성립). 빌드 로그 23:07 → 23:24 CDT, 사이트/추첨/초 = §0. testbed 13:25:08 KST, σ 격자 13:25:33 KST, 일괄 EM 13:25:46 KST, 학습 머리말 13:30:02 KST(split_hash 5ef5dca3dca07cf3, σ [3.3679e-02, 8.5515e-01], 479,426 params), 큐 23:29 CDT, 격자 23:32 CDT, 희소 조정 23:29 CDT — §4 와 일치. 현재 돌고 있는 것: 학습(GPU 2), kron 1024 r2(GPU 1), full 512(GPU 0), `sparse_tune.py --prior SRT`(CPU); 큐 잔여 16 작업.
- 0단계 표(`report_rt.md` 22-44 행): et28/fl28/mu28 `_d2_rs` 의 10 열 모두 §0 표와 일치; **깊이 2·rs 가 세 장면 모두에서 잰 유일한 조합이라는 주장은 참**(etoile·florence 는 그 행만 있다); simple_street_canyon 0.77–0.87, `selection.md` 7·11 행 "실패" ✓.

**읽어서 확인 (Sionna RT 2.1 소스)**
- `Paths.cfr(frequencies=[0], normalize_delays=False, normalize=False)`: `cir()` 가 `a` 에 `exp(−j2π·fc·τ)` 를 곱하고(`paths.py:473-478`; `field_calculator.py` 의 `a` 는 λ/(4π) 스케일만, 전파 위상 없음), cfr 은 f = 0 에서 `Σ_l a_l^b` → **반송파에서의 협대역 채널**. 출력 shape `[num_rx, num_rx_ant, num_tx, num_tx_ant, 1, 1]` → `[:, :, 0, :, 0, 0]` = (UE, Nt, Nr) → `transpose(0,2,1)` = (UE, Nr, Nt), H[a, b] = BS a·UE b = h_dl[b, a] ✓ 상반성.
- `paths.a` (synthetic array 뒤) `[num_rx, num_rx_ant, num_tx, num_tx_ant, paths]` → `[:, 0, 0, 0, :]` = 기준 소자 쌍; synthetic array 는 위상만 바꾸므로(`_apply_synthetic_array`) |a_l|² 는 소자 쌍과 무관 → "기준 소자 쌍의 Σ|a_l|²" = 쌍의 경로 전력 합 ✓. `valid`·`interactions` 는 synthetic 이면 `[num_rx, num_tx, paths]`/`[depth, …]` (`paths.py:848-849`) → `reshape(len(xy), -1)`·`it[0, :, 0, :]` ✓; `InteractionType.NONE = 0` → LoS = 깊이 0 이 NONE 이고 valid ✓.
- `Scene.targets`(`scene.py:867, 1012-1095`): 위치·방향·`array.rotate(λ, o)` 소자 오프셋(수신기 major, 소자 minor)·속도. `rotation_matrix([yaw,0,0])` = Rz(yaw) (`geometry.py:108-122`) → `fast_targets` 의 `[c·x − s·y, s·x + c·y, z]`·reshape 순서 ✓.
- block split 코드 = `dmimo_build.py:90-102` 와 줄 단위 동일(시드만 다름).

**검증하지 못한 것**: selfcheck 수치(콘솔만), san_francisco 탐침, 0단계 "ULA 를 직접 만들었고 스크립트 없음", `logs/tb2_gpu*.log` 내용(의도적으로 열지 않음), `run_srt_base.sh`·`run_srt_post_gpu.sh` 의 실제 실행(§5 뒤), `eval_accept.py`·`pair_*.py` 를 SRT raw 로 돌리는 것(raw 없음), `paper_f33cdf.py` 본문 전체.

## 판정
MUST 2 (M1 GB′ 순서 모순/스크립트, M2 baseline 스크립트의 kron 가정) · SHOULD 10 · NIT 6. M1·M2 는 문장 몇 줄과 스크립트 인자 하나로 닫힌다. 생성기 자체(cfr·상반성·정규화·배열 packing·LoS·split·스트림 매핑)와 §0 수치는 모두 재현·확인됐다. 동결 전 열람 금지는 지금 디스크 상태(fit 3 개, pick 없음)를 동결 줄에 적는 것으로만 뒷받침된다(S6).
