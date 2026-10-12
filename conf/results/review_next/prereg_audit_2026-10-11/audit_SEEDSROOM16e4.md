# Record audit — NEXT_EXPERIMENTS_SEEDSROOM16e4 §5 · §6 (Sionna RT room pools SRB · SRP, seeds a2 · a3) + companion records

- Auditor: Fable 5.1 subagent (independent; read-only on every tracked file). Report written 2026-10-12 13:48 CDT (read by `date`).
- Audited commit: `36022add` (results), run commit = freeze `62c24e7e`. Files read from disk; working tree = HEAD for every audited file (`git status`: only `conf/logs/*` and `conf/results/d2_gbprime_SRP.csv` differ — see S3).
- Method: own numpy reader of the raw npz chunks (6 × 448 files: `raw_{SRB,SRP}B16e4{,s2,s3}`), statistics re-implemented from their written definitions (`recompute_seedsroom.py` → `.out`, 155 lines, `.err` empty): decision points anchored on b\*, exact two-sided sign test (integer binomial sum; scipy `binomtest` as second opinion), power guard, 2/3 rule, SNR@0.1 log-linear crossing + paired bootstrap (B 2000, `default_rng(20260925)`), recovery R + paired bootstrap (`default_rng(20260926)`), Wilson, V0 guard, bit-identity of every array against the a1 raw, per-chunk `run|git` / meta; `torch.load` of 10 checkpoints; GB′ npz. `analysis.load_raw` only as a cross-check of the reader (6 × 686 arrays, 0 differ). Bootstraps use the registered seeds — digit agreement is a reproduction, not an independent sample. Re-runs into own files: the §6.1 generator (`rerun_seedsroom_s6gen.md`), `eval_accept.py` × 8 with the argument forms of `run_seeds16e4.sh` (`rerun_seedsroom_{accept,refarms}_<TAG>.txt`), `paper_f34seed.py` into the scratch folder. Companion records: `recompute_seedsroom_docs.py` → `.out` (number tokens against the cited sources) + per-pool / per-registration checks by hand. CPU only, ≤ 16 threads, nothing written outside this folder and the scratch folder; `conf/code` · `Demo` untouched (`python -B`).
- Counts: registration §0 · §5 · §6 — **152 programmatic comparisons covering ≈ 400 record values, 0 differ**. Companion records — ≈ 870 number tokens checked (EXPERIMENTS row 115, RESULTS §25 414, README section 200, DECISIONS 65, plus 76 phrase checks), **1 differs** (S1).

## Verdict

**Every number, label and prediction score in §5 and §6 of the registration reproduces from the raw data: 0 numeric, label, scoring or acceptance errors.** Both aggregate labels hold by the frozen rule — SRB "시드 강건 (3/3 (i))", SRP "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)"; all four tags are accepted by an independent check (every chunk `run|git` = 62c24e7e without `+dirty`; meta and checkpoint ids as frozen; all 490 non-Stage-C arrays per tag bit-identical to the a1 raw; exactly {V0, V1, V4, V4b} differ; V1 does differ). §1–§3 are untouched since the run commit. §6.1 is byte-identical to the generator's output; the figure and its record re-render byte-identically. The SRP qualifier is present in the registration §6, the EXPERIMENTS row, RESULTS 25.5, the README row and the DECISIONS line; no equivalence or generalisation wording.

**What is wrong or missing: 1 MUST** (an undisclosed departure from the frozen §1: it says "그림 없음", §6.2 reports a figure), **4 SHOULD** (one false number in the DECISIONS end line; a registered report-only quantity missing from §6.1; tracked / cited GB′ result files not in the commit; a README sentence made false by the new figure row), **6 NIT**. No label, number or score changes.

---

## MUST

### M1. §6.2 reports a figure although the frozen §1 says "그림 없음" — the departure is not disclosed
- **Where**: registration §1 row "보고 전용" (frozen at 62c24e7e): "… 그림 없음. 계산하지 않음: …"; §6.2 first bullet "**그림 (보고 전용)**: `conference/figures/F34seed_wide.{pdf,png}` + 기록 `records/paper_f34seed.txt` …"; also the EXPERIMENTS row ("그림 … (보고 전용; 전 점 n 2560)") and the DECISIONS end line ("그림 F34seed_wide").
- **Found**: the figure exists, is correct (counts = raw, 70/70; re-render byte-identical) and tests nothing — but nowhere does the record say that §1 registered no figure, nor why one was made. The instruction is on file: `DECISIONS.md` `[2026-10-12 23:24 KST]` quotes the user "그래프, 피규어 다 그리고 정보도 함께 커밋, 푸시도 하자" — i.e. it predates the freeze (23:26 KST) and §1 was frozen with "그림 없음" anyway. The script was written during the run (`paper_f34seed.py` mtime 13:16:23 CDT; §6.2 third bullet).
- **Add to §6.2** (append-only; new line under the figure bullet):

  > **[감사 M1] 등록과 다른 점**: §1 '보고 전용' 행은 "그림 없음" 으로 동결했다 — `F34seed_wide` 는 등록에 없던 추가 산출물이다(사용자 지시 10-12 CDT '그래프, 피규어 다 그리고 정보도 함께 커밋, 푸시도 하자' — `DECISIONS.md` 10-12 23:24 KST 줄; 동결 전의 지시였는데 §1 에 반영하지 않았다). 등록된 raw 의 실패 수를 그대로 그린 것이고 새 검정·라벨·점 선택은 없다; 스크립트는 실행 중에 썼다.

---

## SHOULD

### S1. DECISIONS end line: runner time range is wrong
- **Where**: `conf/DECISIONS.md`, line `[2026-10-13 03:18 KST] SEEDSROOM16e4 실행 끝·§6 전사`: "(CPU 96 스레드; runner 44–63 분/태그)".
- **Found**: `logs/run_D2_<TAG>.log` "finished in" 44.0 · 45.6 · 58.9 · **64.0** min (= §6.1, §6.2, EXPERIMENTS row). The maximum is 64, not 63.
- **Replacement** (correction line, DECISIONS is append-only): `[감사 S1 정정] 위 03:18 KST 줄의 'runner 44–63 분/태그' 는 '44–64 분/태그' 가 맞다 (44.0 · 45.6 · 58.9 · 64.0 분).`

### S2. §6.1 omits the registered report-only V0 −3 dB BLER
- **Where**: §1 row "보고 전용": "시드별 −3 dB BLER(b\*, V1, V0, genie; …)"; §6.1 gives V1, b\* and genie (as counts) and the V0 guard line, not the V0 BLER.
- **Found** (raw): V0 fails 2560/2560 at −3 dB in all six raws.
- **Add under §6.1 "보고 전용"**:

  > - **[감사 S2]** §1 의 시드별 V0 −3 dB BLER (a1 / a2 / a3; 실패 수 / 2560): SRB 2560 / 2560 / 2560, SRP 2560 / 2560 / 2560 — 모두 1.000. b\* · genie 의 −3 dB BLER 은 세 시드에서 같다: SRB 0.323 · 0.117, SRP 0.530 · 0.167.

### S3. GB′ result files behind §5 / §6.1 are not in the commit
- **Where**: §5 addendum 1 names `results/d2_gbprime_SRB.csv` as its source; §5 addendum 2, §6.1 GB′ lines, EXPERIMENTS row, RESULTS 25.5, README and DECISIONS quote the SRP a2 · a3 medians.
- **Found**: `conf/results/d2_gbprime_SRP.csv` is tracked and **modified-uncommitted at 36022add** (HEAD has the a1 row only; the a2 · a3 rows `…,0.500750,0.973975,0.585981,…` / `…,0.494319,0.993807,0.584032,…` are working-tree only). `d2_gbprime_SRB.csv` and `d2_gbprime_SRB_N160000_a{1,2,3}.npz`, `d2_gbprime_SRP_N160000_a{2,3}.npz` are untracked and not ignored, while the SRP a1 and SRT counterparts are tracked. All 18 quoted values (median / min / max × 6) match the files on disk.
- **Action** (audit-reflecting commit): `git add conf/results/d2_gbprime_SRP.csv conf/results/d2_gbprime_SRB.csv conf/results/d2_gbprime_SRB_N160000_a{1,2,3}.npz conf/results/d2_gbprime_SRP_N160000_a{2,3}.npz`.

### S4. README section opener is false for the row added in this commit
- **Where**: `conference/figures/README.md` § "레이 트레이싱 풀 그림", first paragraph: "모두 8×4 …, Fig. 2 와 같은 범례 11 곡선 (`paper_f16deep.SHOW`), …" and its script / record / registration lists.
- **Found**: `F34seed_wide` (added in 36022add) draws 5 curves (Proposed seed 1 · 2 · 3, GMM prior, Perfect CSI); the lists omit `paper_f34seed.py`, `records/paper_f34seed.txt` and the SEEDSROOM registration. (`F33cdf_*` are CDFs, not 11-curve BLER figures either.) Note for the user's one-legend rule: as drawn, `F34seed_wide` is not a manuscript-legend figure.
- **Replacement** (whole first paragraph):

  > 모두 8×4 (N_r = 8, N_t = 4), N_train = 1.6×10⁵, 고정 풀에서 시험 시행을 복원 추출한다 (새 채널이 아니라 풀의 평균 BLER). BLER 그림 `F21*` 는 Fig. 2 와 같은 범례 11 곡선 (`paper_f16deep.SHOW`); `F34seed_wide` 는 5 곡선 (Proposed 시드 1 · 2 · 3, GMM prior, Perfect CSI — 보고 전용, 원고 범례 그림이 아님); `F33cdf_*` 는 NMSE CDF. 스크립트 `paper_f21dmc.py <PRIOR> [hs|hsx|hsx12]`, `paper_f21room.py [12]`, `paper_f33cdf.py <PRIOR>`, `paper_f34seed.py`; 수치 기록은 `records/paper_f21*.txt` · `records/paper_f33cdf_*.txt` · `records/paper_f34seed.txt`, 등록·결과·감사는 `conf/results/review_next/NEXT_EXPERIMENTS_{DMC16e4,DMCBASE16e4,SRT16e4,ROOM16e4,PATH16e4,FIGHSROOM16e4,FIGHSPATH16e4,FIGHSX16e4,SEEDSROOM16e4}.md`.

---

## NIT

- **N1. "+6 dB 이상은 실패 수가 한 자리"** (§6.2 figure bullet; README `F34seed_wide` row). True for Proposed (≤ 6), Perfect CSI (≤ 1) and the SRB GMM prior (≤ 6); the SRP GMM prior has 29 / 2560 at +6 dB. §6.2 addendum: `[감사 N1] "+6 dB 이상은 실패 수가 한 자리" 는 Proposed · Perfect CSI 곡선의 것이다 (GMM prior 는 SRP +6 dB 에서 29 건).` README cell: `… +6 dB 이상은 Proposed · Perfect CSI 의 실패가 한 자리라 곡선이 흔들린다 (보강 없음). (b) 의 GMM 캐비엇`.
- **N2. "paper 브랜치 동기화 세 번(원격만 갱신)"** (§6.2). Reflog: the local branch ref `paper` moved too (09:26:56 · 09:47:40 · 09:48:07 CDT; pushes 09:27:01 · 09:47:44 · 09:48:10; `git push origin main` 09:27:09; driver log born 09:26:09). HEAD, index and working tree did not move. Addendum: `[감사 N2] "원격만 갱신" = HEAD · 인덱스 · 작업 트리는 그대로, 로컬 \`paper\` 참조와 원격만 갱신.`
- **N3. §6.1 a1 rows are labelled "§0 인용"** but are read from the a1 files by the generator and carry values §0 does not have (per-point and pooled p, b\* · genie counts, R (판정점 합)). All verified from raw. Addendum: `[감사 N3] a1 행은 §0 인용이 아니라 a1 기록 파일 (tables_D2_SR{B,P}B16e4.txt · recovery_SR{B,P}B16e4.txt) 을 같은 생성기로 읽은 것이다 — §0 에 있는 값은 §0 과 같다.`
- **N4. Header: "v2 의 §1 변경은 그 검토의 M1 · S1 · S2 · S4 · N1 문구뿐"** omits N6 — the §1 launch command gained `-c /home/HTJ/t2/conf` and "(시작 뒤 … `start` 줄 확인)" (review N6 quotes v1 without `-c`; §4 lists N6 as applied). A review item, result-neutral. Addendum: `[감사 N4] 머리말의 'v2 의 §1 변경' 목록에 검토 N6 (§1 '태그·실행' 의 tmux -c 와 start 줄 확인) 이 빠져 있다.`
- **N5. RESULTS §25 — stated but in no cited EXPERIMENTS row** (the §25 header says its numbers are verbatim from those rows; every number token of 25.1 · 25.2 was found in its own pool's rows): (a) header "고정 풀 (345,600 쌍 안팎 …)" — only the SRT row has 345,600; DMC row 342,597; the SRB · SRP rows give only the test split (52,353 · 52,200) → `고정 풀 (DeepMIMO 342,597 쌍 · Sionna RT 도시 345,600 쌍; 방 두 풀의 크기는 등록 §5)`; (b) 25.2 last bullet (audit outcome) — the three FIGHS rows say "기록 감사는 이 행을 쓴 뒤"; the source is `prereg_audit_2026-10-11/audit_FIGHS{ROOM,PATH,X}16e4.md` (verdicts agree) → append `(출처: 감사 보고서 — EXPERIMENTS 행에는 없다)`; (c) 25.3 "(Perfect CSI 만으로 선별)" for both room pools — the SRB row says "(Perfect CSI 선별)", the SRP row only "BLER 이 낮도록 고른 풀" → `(SRB 행: Perfect CSI 선별)`; (d) 25.4 `F21room_wide` · `F21room12_wide` — in no cited row (DECISIONS 10-12 23:24 KST line) → append `(두 패널 판은 DECISIONS 10-12 23:24 KST 줄)`; (e) the §25 title does not name SEEDSROOM16e4 → append `; 시드 SEEDSROOM16e4`.
- **N6. WORK_QUEUE head line**: "시드 강건성 (SEEDSROOM16e4: 두 풀 모두 3/3 (i))" gives the SRP label without its qualifier (the detail bullet has it; the subject of commit 36022add has the same short form and cannot be changed). Replacement: `시드 강건성 (SEEDSROOM16e4: SRB 3/3 (i) · SRP 3/3 (i) — SRP 는 b* = 씨앗 초기화 GMM 대비)`.

---

## Verified (how)

**Freeze / git**
- `git diff 62c24e7e 36022add -- <registration>`: one hunk at line 78 — +2 lines (§5 addendum 2 + blank), −1 "(실행 뒤 채운다.)", +§6; §1–§3 and §5 addendum 1 untouched. `git diff --stat` of the two commits touches no file under `conf/code` or `Demo`; `find conf/code Demo -newermt <run start>` empty; driver sha256[:16] 0ce6f000a9d57532 = §4.
- `git log 62c24e7e..36022add` = 36022add only (13:22:21 CDT, after `SEEDSROOM_DONE` 13:16); HEAD reflog has no entry between the two commits (no checkout / reset). §6.2 "no main commit during the run" holds.
- Files with mtime inside the run window: the run's own outputs, the GB′ outputs (10:19 · 11:39 CDT), `s6_seedsroom_gen.py` (11:18:44 CDT — consistent with "11:17 CDT ~ 생성기 시험"), `paper_f34seed.py`; registration / DECISIONS / EXPERIMENTS / RESULTS / README mtimes 13:18 CDT.
- §6.1 = generator output: re-run into `rerun_seedsroom_s6gen.md`, `diff` against the record's 6.1 block empty.

**Raw (own reader; per tag)** — 448 files, chunk plan {(40k, 40)}, k = 0..63, × 7 SNRs; 14 arms; arrays (2560, 16); no `|failed` key.
- `run|git` = {62c24e7e} on all 4 × 448 chunks; `meta|ntrain` 160000; SRB `bstar` gmm1024, `ll_val` 97.00871495382869 (kron_K 2048 placeholder); SRP `bstar` kron, `kron_K` 4096, `ll_val` 244.1932863626755; `stagec_ckpt_id` = §5 sha · epoch · best_epoch · role best, in every chunk; iters 16, seed 20260926.
- Identity vs a1: all 10 non-Stage-C arms × 7 KEYS_RAW × 7 SNRs bit-identical (490 / 490 arrays per tag, NaN-aware, dtype-checked), no key missing; arms differing = exactly {V0, V1, V4, V4b} at every point; extra keys (guardH, clip, diverged, …) differ only for V0 · V1. V1 @16 outcomes differing from a1 (trials per SNR): s2 SRB [165, 55, 8, 4, 2, 0, 0], s3 SRB [172, 55, 14, 1, 4, 0, 0], s2 SRP [123, 61, 15, 4, 0, 0, 0], s3 SRP [132, 55, 20, 4, 0, 0, 0].
- `eval_accept.py` re-run (both forms × 4 tags): first line `ACCEPT: OK -- <TAG>` × 4; `--ref-arms all` reports byte-identical to the record's `_refarms.txt` × 4 (shared 2560/2560 at 7 points).
- Table B `b* → V1`, six raws: decision SNRs −3 / 0 / +3 (b\* BLER SRB 0.3230 / 0.0598 / 0.0156, SRP 0.5297 / 0.1945 / 0.0520; next point 0.0023 / 0.0113); all 18 a:b pairs, 18 per-point p and 6 pooled a:b + p as printed (`%.2g`); ≥ 6 discordant pairs at 3/3 points → POWERED; V1 fewer at 3/3, b\* at 0/3 → (i) × 6 (largest per-point p 0.014, SRB a3 +3 dB) → both aggregates 3/3 (i).
- SNR@0.1 gap and 90 % CI × 6 (4 dp: SRB +0.3209 [+0.1788, +0.4542] · +0.3544 [+0.2239, +0.4837] · +0.3717 [+0.2356, +0.5084]; SRP +2.0051 [+1.7842, +2.2398] · +1.9537 [+1.7286, +2.1820] · +2.1151 [+1.9008, +2.3472]; censored 0 %).
- −3 dB: V1 704 / 711 / 726 and 812 / 829 / 820 with Wilson intervals (same to 3 dp at z = 1.96 and 1.959964); b\* 827 · genie 299 (SRB), 1356 · 428 (SRP) in all three raws; V0 2560 everywhere.
- R(−3 dB) and R(decision points) with CIs × 6; spreads (formed from the printed values, as the record does; unrounded gap spread 0.0508 / 0.1614 dB, R spread 0.0417 / 0.0183); V0 guard lines × 4 (fired / of / rate / worst NMSE).
- §3 scoring, strict: 2 · 5 — 0.278 · 0.284 ∈ [0.258, 0.293], 0.324 · 0.320 ∈ [0.299, 0.335] (also unrounded); 3 · 6 — every CI intersects a1's; 1 · 4 · 7 as above. 7 hits.

**§5** — sha256[:16], epoch, best_epoch of the four `_best.pt`; last `.pt` epoch · sha · stopped_by patience · best_epoch = `_best` epoch; best_val to the last digit; rung · attempt · split_hash (= a1's); a1 `_best` sha · epoch · best_val (§0). GB′: median / min / max × 6 from the npz (ratio nmse_model / nmse_gmm over 20 σ points) = record; times and `rc 0` = `logs/seeds_{SRB,SRP}_train.log`; "last `.pt`, n_eval 4096" = `logs/gbprime_*.log`. SRB a2 · a3 values 09:13 · 09:21 CDT < freeze 09:26:08; SRP 10:19 · 11:39 during the run, pinned to CPUs 69,165 (outside the mask).
- Partial a4 · a5 checkpoints exist (8 files); no raw and no `run_D2_*` / `run_seeds16e4_*` / `analysis_*` log carries those stems — not evaluated.

**§6.2** — driver log `cpus 24-47,120-143,72-95,168-191`; runner minutes 44.0 · 45.6 · 58.9 · 64.0; 09:26 → 13:16 CDT = 3 h 50 min; one `git push origin main` and three paper syncs during the run (second and third carry "미커밋 1" = `docs/RESULTS.md`).

**Figure** — `paper_f34seed.py` with `FIG_OUTDIR=` scratch: PDF, PNG and the record text byte-identical to the committed ones; all 70 counts in the record (5 curves × 7 SNRs × 2 pools) = raw.

**Companion records** — EXPERIMENTS row: every number (times, shas, PID 13 · 15, counts, gaps, BLERs, R, minutes, GB′ medians, review tally) against the registration and logs. RESULTS 25.5: all 73 tokens = §6 / §5 and = the EXPERIMENTS row. RESULTS 25.1: 111 table tokens + 58 bullet tokens each found in its own pool's rows; 25.2: 12 cells + 14 fragments verbatim; 76 phrase checks (N5 lists the misses). README: the two lines added in 36022add (27 tokens) = §6 / figure record; the numbers table against ROOM · PATH · FIGHSROOM · FIGHSPATH · FIGHSX §6 and, for SRB · SRP −3 / 0 / +3 dB BLERs and counts, against raw; derived BLERs (k / 81920) and the 4.7×10⁻⁵ Wilson bound recomputed. DECISIONS freeze line: all values. README's "세 시드 모두 … 유의하게 적게 실패" is true at 3/3 points for every SRB seed.

## Not verified
- That §3 is textually identical in v1 and v2: v1 was never committed and no copy is on disk (session file history searched). What exists: the review header's attestation (sha 9dfba89cd7ec5e0d read 09:07:14 CDT, 6 min before the first GB′ value) and the review's item-by-item description of §3, which matches the committed §3.
- `taskset -cp` reading at start, the mid-run reading times and the report to the user (§6.2), GPU indices, user quotes other than the one in the DECISIONS 23:24 KST line.
- `recovery_ci.py` and `runner.py analysis` were not re-run (re-implemented instead; same digits).
- DMC · SRT numbers in RESULTS 25.1 and the README: checked against the EXPERIMENTS rows / registration text only, not from raw.

## Files (this folder)
`recompute_seedsroom.py` · `.out` · `.err` (empty); `recompute_seedsroom_docs.py` · `.out`; `rerun_seedsroom_s6gen.md`; `rerun_seedsroom_accept_<TAG>.txt` · `rerun_seedsroom_refarms_<TAG>.txt` (× 4) · `rerun_seedsroom_accept_chain.log` (the first chain's parent was stopped by the auditor and the remaining tags run as two chains — hence no rc line for the SRBB16e4s2 refarms call, whose output is complete).
