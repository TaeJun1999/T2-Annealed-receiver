# 기록 감사 — FIGHS16e4 §6.1 (논문 BLER–SNR 그림의 +6..+15 dB 점을 새 시행 n = 20480 으로; 보고 전용, 24 행) — 수치 재계산 + 규칙·출처 감사

- 감사 2026-10-07 17:06 CDT (= 10-08 07:06 KST) (Fable 5.1 서브에이전트, 독립·읽기 전용). 고친 파일 0; 만든 파일은 이 디렉터리의 `recompute_fighs.py`·`recompute_fighs.out`·`audit_FIGHS16e4.md` 셋뿐. 커밋·체크아웃 없음, 삭제 없음, GPU 없음 (`CUDA_VISIBLE_DEVICES=`), 워커 32 (raw 스캔). `~/t2_wtS` 등 다른 워크트리는 열지 않았다. main HEAD 331f6e57 (= 실행 커밋; 뒤 커밋 0; `git status --porcelain conf/code Demo` 0 줄; `DECISIONS.md` 청결).
- 대상: `NEXT_EXPERIMENTS_FIGHS16e4.md` §6.1 (`:206–607`, 미커밋). `git diff 331f6e57 -- <등록>` = hunk `@@ -202,3 +202,406 @@` 1 개, 추가 403 줄·삭제 0; `:1–204` (`## 6. 결과 (이 절은 추가만 한다)` 까지) 는 커밋본과 줄 단위 동일.
- 방법 (`recompute_fighs.py` → `recompute_fighs.out`, 65 검사 묶음, FAIL 0): raw npz 를 numpy 로 직접 열어 재계산 — 새 raw 24 × 2048 = 49,152 청크 (이름·`run|*`·`meta|*`·arm 별 `blk_err` 마지막 열 (비유한 = 실패)·반복 1 열·`|failed`·mtime, genie 재현은 REF 청크를 같이 열어 배열 비교), 원 raw 26 × 448 = 11,648 청크, 대조 raw `FHC` 96·`ZZ` 96 청크, ALD npz 6 개. Wilson 은 따로 구현 (z = 1.959963984540054), Fisher 는 `scipy.stats.fisher_exact(alternative='greater')`. `s6_gen.py`·`analysis.load_raw`·`hisnr_report` 는 호출하지 않았고 집계표는 입력이 아니라 비교 대상으로만 읽었다. 그 밖은 로그 (`run_fighs16e4.log`, runner 로그 24 + FHC 24 + ZZ 24, `recover.log`, `figs_pushed.txt`, `before/` + `before.sha256`), 수용·대조·집계·매니페스트 파일, 그림 기록 7 개와 스크립트 7 + `fighs_merge.py`, git (reflog·paper 브랜치·`git diff --quiet paper -- <png>`), 환경 (`hostname`·`ps -o lstart= -p 1`·`uptime`·`nvidia-smi`·`ldd`·apt 기록) 과의 대조.

## 총평

**판정: §6.1 의 수치·채점·인용 오류 0 (재계산 65 검사 묶음 전부 통과 — 세부 비교: 집계표 400 행 + Wilson 400 칸, §6.1 보고 표 336 칸 + genie 줄 8, 예측 칸 304 (tsv 304 행 × 13 필드)·구간 밖 23·§0.4 76 곡선·오르는 칸 15/9/0·Fisher 8 행 + 그림 기록 129 곡선 줄 (k/n 516) 의 rising 전부 재계산·예측 3 24 칸, genie 재현 36,864 청크 × 4 키, 대조 2632 + 2632 (chunk, arm, key) + ALD 3 배열 × 2, 행별 표 24 × 7 필드, 매니페스트 24 × 12, 대조 표 26 줄, before/ 39 해시, 청크 mtime 49,152; 불일치 0), 규칙 위반 0. MUST 0 · SHOULD 3 (편차 목록 누락 1, 출처 추적성 1, 문구 모순 1) · NIT 6 — 수치·채점 불변.**

## MUST (틀린·근거 없는 수치 / 규칙 오적용)

**없음.**

## SHOULD (완전성·출처·문구; 수치·채점 불변)

1. **[편차 목록 누락 — 범위 밖 패널의 축 변경] §6.1 '편차·주의' 의 '**그림**' 항목 (`:606`)** — 범위 밖으로 선언된 F24 (a)(b) (도플러; §1 "범위 밖: … F24 의 도플러 (a)(b)") 의 y 축 아래 한계가 2e-4 → 3e-5 로 함께 바뀌었다 (`paper_f24.py:120` 패널마다 `set_ylim(2e-4, 1.05)` 뒤 `:130` 에서 공유 y 축 `axs.flat[0].set_ylim(3e-5, 1.05)`, `sharey=True`; 데이터 불변). F16 (a) 의 범례 상자도 OMP 곡선을 비켜 오른쪽으로 옮겼다 (축 비율 x 0.38 → 0.44). 둘 다 `conference/figures/README.md` 'FIGHS16e4 merge' 절에는 적혀 있으나 §6.1 에는 없고, 같은 §6.1 의 '실행 중 결과 열람·공개' 항목은 "그림 규칙은 바꾸지 않았다" 로 끝난다.
   - 고칠 문구 ('그림' 항목 끝에 덧붙임): " 범위 밖 패널 F24 (a)(b) 는 y 축을 (c)(d) 와 공유하므로 아래 한계가 2e-4 → 3e-5 로 같이 바뀌었다 (`paper_f24.py:130`; 데이터·점 불변); F16 (a) 의 범례 상자는 OMP 곡선을 비켜 오른쪽으로 (x 0.38 → 0.44). 둘 다 README 'FIGHS16e4 merge' 에 적힌 표시 변경이며 §1 그림 규칙의 점·n·막대·화살표 규칙은 그대로다."
2. **[출처 추적성 — 드라이버 이전 값] '편차·주의' 첫 항목 (`:597`) "그 전 값으로 남아 있는 기록은 `CLAUDE.md` 의 580.173.02 다"** — 기록 시점 (16:23 CDT) 에는 맞았으나, 작업 트리의 `CLAUDE.md` 는 그 뒤 16:26 CDT (mtime 10-08 06:26:05 KST) 에 미커밋으로 고쳐져 지금은 "드라이버 580.178.04 … 2026-09-16 기록은 580.173.02 였고 언제 바뀌었는지는 기록이 없다" 로 읽힌다. 580.173.02 가 적힌 판은 커밋 331f6e57 의 `CLAUDE.md` 이고, conf/logs·results 어디에도 중단 전 드라이버 값을 담은 로그는 없다 (grep `580.173` 0 건; 이 감사 확인) — "CLAUDE.md 에만 있다" 는 사실은 맞다.
   - 고칠 문구: "그 전 값으로 남아 있는 기록은 커밋 331f6e57 의 `CLAUDE.md` (2026-09-16 기록) 의 580.173.02 뿐이다 (conf 의 로그·결과 파일 어디에도 중단 전 드라이버 값 없음; 중단 직전에 읽은 값은 없다; 작업 트리의 `CLAUDE.md` 는 이 기록 뒤 16:26 CDT 에 새 값으로 고쳤다)".
3. **[문구 모순 — '실행 구간'] '편차·주의' 둘째 항목 (`:598`) "이 검사는 두 시작 사이에 돌았고 (실행 구간 밖)"** — 같은 §6.1 이 '실행 구간' 을 "첫 시작 ~ FIGHS_DONE" (`:547`) 으로 정의하고 '소요' 도 그 벽시계 (20.70 h) 를 적는다. 환경 검사 (21:08:00–21:15:03 CDT; `raw_ZZ*` 청크 mtime 21:08:09–21:14:55 CDT) 는 그 정의로는 구간 **안**이고, 다만 runner 가 돌지 않던 틈 (중단 20:37 ~ 재개 21:15 CDT) 에 있었다는 뜻이다.
   - 고칠 문구: "(실행 구간 밖)" → "(첫 시작 ~ FIGHS_DONE 구간 안이지만 FH runner 가 돌지 않던 틈 — 중단 20:37 ~ 재개 21:15 CDT — 에서; `raw_ZZ*` 청크 mtime 21:08–21:15 CDT)".

## NIT (표기·보강)

1. **`:224` "(`before/`, 37 파일; sha256)"** — `before/` 에는 39 파일이 있다 (`recover.log` "backup: 39 files", `before.sha256` 39 줄; 해시 전부 일치). 생성기가 재개가 **덧붙이는** 두 로그 (`run_fighs16e4.log`·`fighs_tmux.out`) 를 비교에서 뺀 37 이다. → "(`before/` 39 파일 중 재개가 덧붙이는 로그 2 개를 뺀 37 파일; sha256)".
2. **`:563–574` '묶음별 runner 분' 표의 "§1b 추정 (min)" 열 (57/146/78/248/250/51/51/255)** — 등록 §1b 의 묶음 표 (`:163–165`) 는 58/145/78/247/250/51/51/256 이다. §6.1 값은 §1b 행별 정수 (≤ 는 수로) 의 합이고 §1b 묶음 표는 반올림 전 값의 합이라 ±1 다르다. → 열 머리를 "§1b 행별 추정의 합 (min)" 으로 하고 각주 "(§1b 묶음 표 자체는 58/145/78/247/250/51/51/256)".
3. **`:597` "원인은 기록자가 알지 못한다 (서버 쪽 일)"** — 괄호가 근거 없이 원인의 소재를 적는다. 증거는 PID 1 시작 시각 (20:38:41 CDT), hostname 변화 (매니페스트 `0695aede856d` → `262d04c812cc`), 호스트 uptime (재부팅 없음) 뿐이다. → "(근거: 컨테이너 PID 1 시작 시각·hostname 변화·호스트 uptime; 누가·왜 다시 만들었는지는 기록 없음)".
4. **`recover.sh:2–3` 머리 주석 (§6.1 이 '중단·재개 기록' 의 출처로 인용하는 파일)** 은 "old container 9000babdde68 → 262d04c812cc; host NVIDIA driver 580.173.02 → 580.178.04" 라 적는데, 앞 값 둘은 당시 `CLAUDE.md` 의 값이고 중단 전 컨테이너의 hostname 은 매니페스트대로 `0695aede856d` 다 (`9000babdde68` 은 더 이른 컨테이너). §6.1 본문은 매니페스트 값을 바르게 쓴다. → '중단·재개 기록' 머리에 한 구절: "(`recover.sh` 머리 주석의 이전 컨테이너 id `9000babdde68`·드라이버 580.173.02 는 당시 `CLAUDE.md` 값; 중단 전 hostname 의 증거는 `before/` 매니페스트의 `0695aede856d`)".
5. **`:547–561` '실행 구간 … 다른 CPU 작업'** — (a) 생성기는 두 세션 파일의 **끝 12 MB** 만 읽었다 (`s6_gen.py:343–346`); 그 범위 밖의 호출은 목록에 없을 수 있다 (세션 파일은 `~/t2` 밖이라 이 감사는 열지 않았다 — 검증 불가; 간접 확인: `figs_pushed.txt` 의 paper 커밋 6 개의 커밋 시각이 목록의 `sync_paper_branch.sh` 시각과 분 단위로 일치, HEAD reflog 에 실행 구간의 HEAD 이동 0). (b) 재개 구간 내내 살아 있던 세션 기반 프로세스 — `chroma-mcp` (claude-mem 플러그인; PID 2633, 시작 10-06 20:58 CDT, 10-07 17:00 CDT 시점 누적 CPU 2 h 52 min ≈ 0.14 코어)·`claude` (PID 3556, 누적 38 min) — 는 목록에 없다 (HISNR §6.2 메모와 같은 "하한"). (c) "감시 브리핑은 BLER 수를 읽지 않았고" (`:602`) 는 저장소 안의 증거로 확인할 수 없는 기록자 진술이다. → 목록 머리에 "(세션 파일 끝 12 MB 만 읽음; 세션 자체의 상주 프로세스 — chroma-mcp·claude — 는 제외; 하한)" 을, (c) 에 "(세션 기록 기준; 저장소 증거 없음)" 을 붙인다.
6. **`:606` '그림' 항목 — 그림 코드의 상태 미기재** — `fighs_merge.py` (미추적) 와 `paper_f16/17/20/21/22/24/31.py` (수정) 는 전부 실행 시작 **전** (mtime 10-06 19:06–19:22 CDT; 실행 커밋 19:30 CDT 에 들어가지 않음) 에 쓰였고 main 에는 아직 미커밋이며 paper 브랜치 adb8a752 ("main 331f6e57 + 미커밋 25") 에 동기화돼 있다; `records/` 도 미추적. → "스크립트·`fighs_merge.py` 는 실행 시작 전 (10-06 19:06–19:22 CDT) 에 쓰였고 실행 중 바뀌지 않았다 (mtime); main 미커밋, paper adb8a752 에 동기화" 한 구절.

## 규칙 적용 검사 (등록 §1–§3, 실행 커밋 331f6e57; 위반 없음)

1. **append-only·커밋**: `:1–204` = 커밋본 ✓, 추가 403 줄·삭제 0 ✓; HEAD = 331f6e57 (2026-10-06 19:30 CDT) ✓, 뒤 커밋 0 ✓; HEAD reflog 의 마지막 이동 = 그 커밋 (09:30:13 KST) — 실행 구간에 HEAD 이동 0 ✓ (`sync_paper_branch.sh` 는 임시 index + `commit-tree` + `update-ref refs/heads/paper` 로 HEAD 를 건드리지 않는다 ✓); conf/code·Demo 청결 ✓.
2. **전제·행·n·SNR**: 24 행 전부 실행·수용 (`FIGHS_DONE ok=24 fail=0`; 로그 ABORT/INVALID/SKIP/FAILED/rc≠0 0) ✓; 모든 태그 2048 청크 = 4 SNR × skip 10000..30440 step 40 × n 40, `run|git` 331f6e57 (+dirty 0), `run|iters` 16, `run|seed` 20260926 ✓; meta ntrain·b\*·kron_K·ll_val·ckpt sha+role (SP 행은 ckpt id 없음)·`meta|sparse` = pick 의 그 SNR·`meta|rotation` `deg=15.0:`/`deg=30.0:`·`meta|ald_file` = 경로 + sha256[:16] (d962c0b6cf7e47a6·bc23a889d2521ec0) ✓; raised 0 (`|failed` 합 0, 비유한 0) ✓; ckpt 6·pick 6·ALD 기록 8 의 sha = §1a/§5 ✓.
3. **genie 재현 (a)**: REF 가 있는 18 행 × 2048 청크 × 4 키 (blk_err·ber·tauL_gmean·alphaD) 전부 비트 동일 ✓ (D2 C2 3 행 ↔ `raw_HSB16e4k`, D2 C6 3 행 ↔ `raw_HSNR16`, 나머지 ↔ 같은 데이터셋·조건의 첫 행). 회전 행 genie 는 HSB16e4k 와 다르다 (71/36/19/18 대 66/36/16/13; 등록 §0.3 대로 대조 대상 아님).
4. **대조 (phase C)**: `raw_FHC*` 24 × 4 청크 ↔ ORIG raw, 모든 arm × KEYS_RAW 7 — 2632 비교, 다름 0 (NaN = NaN) = `*_control.txt` 24 의 수·`CONTROL: OK` ✓; ALD 추정기 대조 2 — hhat (7, 2560, 32)·b·v 비트 동일, 최대 |차| 0, `CONTROL-ALD: OK` ✓; 등록 밖 환경 검사 `raw_ZZ*` ↔ `raw_FHC*` 2632 비교 다름 0, 다른 키는 `meta|em_sec_note` (적합 링크 경로가 태그 이름을 담음) 뿐 ✓ = §6.1.
5. **중단·재개 (§1)**: 같은 커밋의 `start` 줄 2 개 ✓; `--resume` 가 읽을 수 없는 청크 0 ✓ (`raw_FH*.truncated` 없음); 대조·수용·집계 다시 실행 ✓ (FHC runner 로그 24 = 머리 2 + done 4 + exists 4; ALD 대조 추정은 새 컨테이너에서 다시 계산 — mtime 11:15:40/11:16:15 KST, sha 중단 전과 동일); 1–3 행 exists 2048·재수용 ✓, 4–24 행 재개 구간에서 처음 계산 ✓ — **청크 mtime 으로 독립 확인**: 1–3 행 19:43–20:36 CDT (컨테이너 재생성 20:38:41 이전), `raw_FHD3B16e4` 최초 청크 21:25 CDT (재개 run 줄 21:19 뒤; 첫 구간 runner 로그 done 0·exists 0·`finished in` 없음), 20:36–21:19 CDT 사이에 `raw_FH*` 에 쓰인 청크 0, 모든 행의 청크 mtime 이 자기 run 줄 ~ acceptance 줄 안; TAG 부분집합 없음 (24 행) ✓; 끝난 태그 재실행 없음 ✓.
6. **실행 환경 (§1 '실행')**: CPU 전용 (runner 로그에 GPU 사용 없음), GPU 는 ALD 추정기 대조 (phase C, GPU 0, 차례로) 와 새 시행 ALD 추정 (phase R, GPU 0) 에서만 ✓; 산출물 수 = §1 (raw 24·대조 raw 24·control 24·aldcontrol 2·accept 24·fighs 24·manifest 24·적합 링크 48·ALD FHC 판 8·hisnr ALD 4) ✓; "main 커밋 없음" ✓; "실행 중 다른 CPU 작업 없음" 과 다른 점 — §6.1 목록 (그림 스크립트·paper 동기화·s6_gen 시험·감시) + 위 NIT 5 (b) 의 상주 프로세스; conf 안에서 실행 구간에 바뀐 파일은 FH 산출물뿐 (`find -newermt`; 미커밋 로그 `fit_D2_n16e4.log`·`queue.log`·`train_*.log` 는 10-04/10-05 KST 의 것) ✓.
7. **보고 (§1 '보고')**: 집계표 24 — 머리말 `load_raw warnings 0`, 모든 arm @16 + 별칭 `R0-pilot@1` (반복 1; 6 행) ✓, Wilson z = 1.959964 ✓; 검정·라벨 없음 ✓ (§6.1 의 ✓ 는 등록 §3 의 적중/빗나감 채점).
8. **그림 규칙 (§1)**: 7 스크립트 — −3/0/+3 dB 원 raw, +6..+15 dB 는 `fighs_merge.merge` 가 `raw_FH<원 태그>`/HISNR raw 에서 (한 점 = 한 raw) ✓; 새 raw 의 k/n 을 집계표와 assert (`fighs_merge.py:110`) ✓; 오차 막대는 F16 (a) 네 arm (`paper_f16.py:98`)·F17 (`:153`)·F20 (b) (`:118`) 에만, 점마다 자기 n (`wilson(k, n)`) — F16 (a) 희소 3 곡선 (`:111` plot)·F21·F22·F24·F31 (b) 는 막대 없음 ✓; 실패 0 점은 곡선 끊김 (NaN) + genie 는 `zero_arrows` (1.96²/(n + 1.96²): 2560 → 1.498e-3, 20480 → 1.875e-4) ✓; y 축 아래 한계 F16 (a)·F20 (b)·F21·F22·F24·F31 (b) 3e-5, F17 4e-5 ✓ (F24 (a)(b) 의 공유 축 부작용은 SHOULD 1); 평활·재실행·점 빼기 없음 ✓; 기록 텍스트 7 — 'FIGHS16e4 merge' 블록의 k/n 516 = 집계표 (`fighs_`/`hisnr_`) = raw ✓, `rising:` 줄 10 (f21 7·f22 1·f24 2) 의 칸·단측 Fisher p 를 −3..+15 dB 전 구간에서 재계산해 글자 동일 ✓ (`+3->+6` 칸은 두 시행 집합 비교), FALLBACK/WARNING/"n = 2560 over the whole range" 0 ✓; paper 브랜치의 PNG 9 개 = 다시 그린 PNG (`git diff --quiet paper`) ✓, 기록 파일 mtime 16:16–16:18 CDT (FIGHS_DONE 16:12 뒤) ✓.
9. **예측 (§3)**: 1 — 304 칸 중 281 안 (0.9243 ≥ 0.90) ✓, 구간 밖 23 칸 목록 글자·수 동일 ✓, 묶음 표 8 ✓; 2 — 원 raw 오르는 곡선 R3 제외 9/70 (목록 9 개 동일), 전체 15/76 = §0.4 ↑ 15 ✓, 새 raw 0/70 ✓, 오르는 칸 표 8 행 (R3 7 + SV8e genie +3→+6 1) 의 수·p (0.00057·0.24·0.89·0.00014·0.00036·0.43·0.00033·0.0096)·표기 ✓; 3 — 24 칸 중 23 (SV8e +12 dB V1 1 > b\* 0) ✓; 분모 304·70·24 (76 곡선 전부 수용) ✓; 합계 적중 3·빗나감 0 ✓.
10. **전사만 (§6.1 머리말)**: 본문 (`:208–594`) = `s6_draft_raw.md` 출력과 비어 있지 않은 336 줄이 글자 동일 ✓ (HTML 주석 줄은 들어가지 않음); 손으로 쓴 '편차·주의' 의 수 — 20:37·20:38:41·0695aede856d·262d04c812cc·580.173.02·580.178.04·37 (NIT 1)·24·2632·0·34·3·`be03…`·`6534…`·`d962…`·`bc23…`·4d05…·1ea3…·1151·18–22 h·9 개 PNG·9/70·304·70·24 — 전부 추적됨; 해석 어휘 ("우수·시사·입증·결론·유의하게") 0; 판단 문구는 "소요에는 영향이 있을 수 있다" (`:601`, 유보 문장) 와 NIT 3 의 괄호뿐.
11. **환경 문장 (`:541–545`)**: hostname·PID 1 시작 (`화 10월  6 20:38:41 2026` CDT)·드라이버·glibc·apt 마지막 Start-Date — 지금 읽은 값과 동일 ✓ (uptime 은 시간 경과분만 다름); 중단 전 매니페스트 versions = `before/run_manifest_FHB16e4k.json` 그대로 ✓; 컨테이너 재생성 시각 20:38:41 은 마지막 로그 줄 20:37 과 복구 시작 21:08:00 사이 ✓; "호스트는 재부팅되지 않았다" ← uptime 1 주 2 일 ✓. 사실 서술 강도: 원인 미상으로 적음 ✓ (NIT 3 의 괄호만 제외).

## 검사 표 (`recompute_fighs.out`; 전부 PASS)

| 검사 | 비교 수 | 불일치 |
|---|---|---|
| A 등록 ↔ ROWS (태그 24, REF/ORIG/플래그/ckpt·pick sha) · 디스크 sha (ckpt 6·pick 6·ALD 8) | 24 행 + 20 파일 | 0 |
| B 새 raw 24 × 2048: 이름·`run|snr/skip/n/iters/seed/git`·cell·prior·arm 집합·shape·meta 8 종·raised | 49,152 청크 | 0 |
| B7 genie 재현 (REF 18 행 × 2048 청크 × blk_err·ber·tauL_gmean·alphaD) | 147,456 배열 | 0 |
| C 원 raw 26 × 448: 연속성 (skip 0..2520)·n 2560·실패 수 | 11,648 청크 | 0 |
| D1 수신기 대조 FHC ↔ ORIG (arm × KEYS_RAW, NaN = NaN) = control.txt 24 | 2632 | 0 |
| D2·D3 환경 검사 ZZ ↔ FHC = cmp_ZZ*.txt 24, 다른 키 = {`meta|em_sec_note`} | 2632 | 0 |
| D4 ALD 추정기 대조 2 (hhat·b·v) | 6 배열 | 0 |
| E1·E2 집계표 24: 실패/n (R0-pilot@1 포함) · BLER·Wilson 문자열 | 400 + 400 | 0 |
| E4·E5 §6.1 보고 표 (실패 · BLER) + genie '같은 수' 8 줄 (태그 24 포괄) | 336 칸 | 0 |
| F1–F4 예측 1: 304 칸·묶음 표 8·구간 밖 23 · `fighs_cells.tsv` 304 행 × 13 | 304 + 23 + 304 | 0 |
| F5–F8 §0.4 원 실패 수 76 곡선·↑ 15·예측 2 (9/70, 0/70)·오르는 칸 표 8 (Fisher p) | 76 + 15 + 8 | 0 |
| F9 예측 3 (6 × 4 칸, 23/24) | 24 | 0 |
| G1–G8 실행 로그 (시작 2·phase C·행 24·FIGHS_DONE·ABORT 류 0)·runner 로그 24 (머리·done·exists·분)·행별 표 24 × 7·분 합 1166.4·묶음 8·소요 18.95/20.70 h | 24 × 7 + 8 + 3 | 0 |
| G9–G10 대조 표 26 줄 · 매니페스트 표 24 × 12 (+ written ↔ acceptance ≤ 3 min) | 26 + 288 | 0 |
| G11–G14 before/ 39 해시·34/3·매니페스트 차이 키 2·ALD 대조 sha/mtime·새 시행 ALD sha/mtime/prov | 39 + 3 + 4 | 0 |
| G15–G17 recover.log 6 줄·figs_pushed 7 줄 인용 · paper 커밋 6 (시각·브랜치) | 13 + 6 | 0 |
| G18–G21 청크 mtime (FH 49,152·FHC 96·ZZ 96) ↔ 중단·재개 창 · FHC 로그 24 · FHD3B16e4 두 구간 | 49,344 | 0 |
| G22–G24 등록 동결부 204 줄 · HEAD/청결 · PNG 9 = paper | 204 + 9 | 0 |
| H1–H2 그림 기록 7: k/n 516 · rising 129 줄 재계산 · 금지 문구 0 · §6.1 인용 10 줄 + 머리 7 | 516 + 129 + 17 | 0 |
| I1–I5 환경 5 값 · 재생성 시각 순서 · CLAUDE.md 두 판 · 기록 시각 · 본문 = 생성기 출력 336 줄 | 5 + 336 | 0 |

## 메모 (정정 아님)

1. 등록 §1b 의 "+ 재생성 차이" 와 실측: UMi28·MIX3 묶음의 runner 분 (297.5·302.7) 이 §1b 행 합 (248·250) 보다 크고 나머지 묶음은 작다 — §6.1 은 수만 적었다 (해석 없음, 등록 §1 "전부 부하에서 1.5–2 배면 +1.6–3.3 h" 범위 안).
2. 환경 검사의 runner 24 개 (`envchk/run_ZZ*.log`) 는 행마다 1.6–6.8 min, 전부 21:08–21:15 CDT 에 병렬 — `raw_ZZ*`·`gmm_fits_D2_ZZ*` 24 + 24 는 지금도 있다 (§6.1 "기록 감사 뒤 지운다").
3. `FHPILB16e4k` 재개 구간의 `finished in 0.1 min` (exists 2048) 은 §6.1 의 합산 규칙 (0.5 min 미만 제외) 대로 빠졌다; 1–3 행의 재개 구간은 모두 exists-only 다.
4. 등록 §5 'ALD 기록 sha256[:16]' 행의 끝 "재확인 값:" 은 비어 있다 (동결부라 고치지 않음; 값은 이 감사 A5 가 재확인 — 8 개 전부 §5 와 일치).
5. 기록 시각: §6.1 머리 16:23 CDT, 생성기 산출물 mtime 06:22 KST (= 16:22 CDT), `README.md` 16:27 CDT, `CLAUDE.md` 16:26 CDT — 기록 뒤의 두 편집은 §6.1 밖.

## 검증하지 못한 것

- '실행 구간 … 다른 CPU 작업' 의 시각 10 건·사용자 지시 메시지 (10-06 19:57 CDT)·"감시 브리핑은 BLER 수를 읽지 않았고": 출처가 `~/.claude/projects/-home-HTJ-t2/*.jsonl` (저장소 밖) 이라 열지 않았다; 간접 증거 (paper 커밋 시각·HEAD reflog·기록 파일 mtime) 는 모두 일치.
- 재개가 tmux 안에서 돌았는지: 컨테이너 재생성으로 당시 tmux 는 없고, 지금의 tmux 세션 `dev` 는 10-06 20:58 CDT 에 만들어졌다 (`recover.sh` 는 `fighs_tmux.out` 에 덧붙임).
- 중단 전 컨테이너의 드라이버 값: conf 안에 기록 없음 (SHOULD 2 대로 `CLAUDE.md` 커밋본뿐).

## §6.2 제안 문단 (주 세션이 §6 에 추가할 때 그대로 쓸 수 있는 문안; 시각은 이 감사가 끝날 때 `TZ=America/Chicago date` 로 채운 값)

### 6.2 기록 감사 (수치 재계산 + 규칙·출처 감사, Fable 5.1 서브에이전트, 독립·읽기 전용; 2026-10-07 17:06 CDT (= 10-08 07:06 KST); `prereg_audit_2026-10-07/audit_FIGHS16e4.md` (`recompute_fighs.py/.out`); raw npz 에서 독립 재계산 — s6_gen·analysis.load_raw·hisnr_report 미호출, 집계표는 비교 대상)

수치·채점·인용 오류 **0** (65 검사 묶음, 불일치 0), 규칙 위반 **0**. 다시 계산한 것: 새 raw 24 × 2048 청크 (시행 계획 10000..30440 × 40 × 4 SNR, `run|git` 331f6e57·iters 16·seed, meta ntrain·b\*·kron_K·ll_val·ckpt sha/role·sparse = pick·rotation·ald_file sha, raised 0, genie 재현 18 행 × 2048 × 4 키 비트 동일); 집계표 24 (400 행·Wilson 400) 와 §6.1 보고 표 336 칸·genie 줄 8; 원 raw 26 (448 청크 연속·n 2560) 로 76 곡선 × 4 칸 — 예측 1 281/304·구간 밖 23·`fighs_cells.tsv` 304 행, §0.4 76 곡선·↑ 15, 예측 2 9/70 → 0/70·오르는 칸 8 (Fisher p), 예측 3 23/24; 대조 FHC ↔ ORIG 2632·ZZ ↔ FHC 2632 (다른 키 `meta|em_sec_note` 뿐)·ALD 추정기 대조 2; 실행 로그·runner 로그 24·행별 표·분 합 1166.4·소요·대조 표 26·매니페스트 24·before/ 39 (34 동일·3 매니페스트 host/written)·ALD sha/mtime; 청크 mtime 으로 중단·재개 독립 확인 (1–3 행 20:38:41 CDT 이전, 4–24 행 21:19 이후, 틈에 쓰인 청크 0); HEAD reflog 이동 0·paper 커밋 6·PNG 9 동일; 그림 기록 7 의 k/n 516·rising 10 줄 재계산·스크립트의 §1 규칙. 정정 SHOULD 3 (수치 불변): (1) 편차 목록에 범위 밖 F24 (a)(b) 의 y 축 3e-5 (공유 축)·F16 (a) 범례 이동 추가; (2) 드라이버 이전 값의 출처를 "커밋 331f6e57 의 `CLAUDE.md` (2026-09-16 기록)" 로 (작업 트리 `CLAUDE.md` 는 기록 뒤 16:26 CDT 에 새 값으로 고쳐짐); (3) 환경 검사 "(실행 구간 밖)" → "첫 시작 ~ FIGHS_DONE 안의 runner 가 없던 틈 (20:37–21:15 CDT)". NIT 6 (before/ 37 → 39 중 37; §1b 묶음 열 ±1; "(서버 쪽 일)" 괄호; `recover.sh` 머리의 이전 컨테이너 id 는 CLAUDE.md 값; 다른 CPU 작업 목록은 세션 파일 끝 12 MB 기준·상주 프로세스 chroma-mcp/claude 제외·감시 진술은 저장소 증거 없음; 그림 코드 미커밋 상태). 메모: 세션 기록 (`~/.claude/projects/…jsonl`) 은 저장소 밖이라 열지 않았다 — 간접 증거 일치.

**MUST 0 · SHOULD 3 · NIT 6.**
