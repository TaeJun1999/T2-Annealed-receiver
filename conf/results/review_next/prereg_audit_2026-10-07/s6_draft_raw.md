<!-- s6_gen.py draft: 24/24 count tables present; missing none -->

**실행·수용** (`logs/run_fighs16e4.log` 의 줄 그대로; 시각 CDT)

- 시작 1: `[fighs 10-06 19:30 CDT] start (git 331f6e57) rows: all resume=0 skip0 10000 n 20480 SNR 6 9 12 15` — phase C `24 receiver control(s) OK, 2 ALD estimator control(s) OK` (10-06 19:38) — FIGHS_DONE 줄 없음; 이 구간의 ABORT/INVALID/SKIP/FAILED/rc≠0 줄 0
- 시작 2: `[fighs 10-06 21:15 CDT] start (git 331f6e57) rows: all resume=1 skip0 10000 n 20480 SNR 6 9 12 15` — phase C `24 receiver control(s) OK, 2 ALD estimator control(s) OK` (10-06 21:16) — 끝 `FIGHS_DONE ok=24 fail=0` (10-07 16:12); 이 구간의 ABORT/INVALID/SKIP/FAILED/rc≠0 줄 0
- `--resume` 의 청크 검사 줄: ['[fighs] resume: 0 unreadable chunk file(s) moved aside']

**중단·재개 기록** (`logs/fighs_interrupt_20261006CDT/recover.log` 그대로)

    [recover 10-06 21:08:00 CDT] start: host 262d04c812cc, driver 580.178.04 , ldd (Ubuntu GLIBC 2.39-0ubuntu8.7) 2.39, git 331f6e57; run log ends: [fighs 10-06 20:37 CDT] FHD3B16e4 run: --testbed
    [recover 10-06 21:08:00 CDT] backup: 39 files -> logs/fighs_interrupt_20261006CDT/before/ (sha256 in logs/fighs_interrupt_20261006CDT/before.sha256)
    [recover 10-06 21:08:00 CDT] envchk: recomputing the 24 receiver controls (test chunk 0 = trials 0..39 at 6 9 12 15 dB) under scratch tags ZZ<row>
    [recover 10-06 21:15:03 CDT] envchk done: 24/24 rows bit-identical to the old-container control raws
    [recover 10-06 21:15:03 CDT] resume: bash code/run_fighs16e4.sh --resume (output appended to logs/fighs_tmux.out)
    [recover 10-07 16:12:53 CDT] run_fighs16e4.sh --resume exited rc=0; run log ends: [fighs 10-07 16:12 CDT] FIGHS_DONE ok=24 fail=0

- 환경 검사 (등록 밖; 스크래치 태그 `ZZ<행>`, 시험 청크 0 = 시행 0..39, +6/+9/+12/+15 dB): 비교 파일 24, `ENVCHK: OK` 24, (청크, arm, 키) 비교 2632, 다름 0; 파일 전체에서 다른 키 (정보용): ['meta|em_sec_note']
- 재개가 다시 만든 산출물 대 중단 전 사본 (`before/`, 37 파일; sha256): 바이트 동일 34, 다름 3 ['run_manifest_FHB16e4k.json', 'run_manifest_FHPILB16e4k.json', 'run_manifest_FHSPB16e4k.json']
    - `run_manifest_FHB16e4k.json`: 다른 키 ['versions', 'written']; versions: {"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "0695aede856d", "cpu_count": 192} → {"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "262d04c812cc", "cpu_count": 192}; written: "2026-10-07 10:36:39 KST" → "2026-10-07 11:18:35 KST"
    - `run_manifest_FHPILB16e4k.json`: 다른 키 ['versions', 'written']; versions: {"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "0695aede856d", "cpu_count": 192} → {"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "262d04c812cc", "cpu_count": 192}; written: "2026-10-07 10:33:55 KST" → "2026-10-07 11:17:36 KST"
    - `run_manifest_FHSPB16e4k.json`: 다른 키 ['versions', 'written']; versions: {"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "0695aede856d", "cpu_count": 192} → {"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "262d04c812cc", "cpu_count": 192}; written: "2026-10-07 10:28:14 KST" → "2026-10-07 11:16:35 KST"
    - `ald_FHCXAROTaB16e4k.npz` sha256[:16] 중단 전 be03f8de6de67c10 · 지금 be03f8de6de67c10 (mtime 10-07 11:15:40 KST)
    - `ald_FHCXAROTbB16e4k.npz` sha256[:16] 중단 전 6534bb27258fa42b · 지금 6534bb27258fa42b (mtime 10-07 11:16:15 KST)
- 그림 스크립트 실행 (실행 구간 중; `figs_pushed.txt` 그대로):
    F17 | 2026-10-06 20:02 CDT | 6d90dee4 | previous session (HISNR raws only)
    F16 | 2026-10-06 20:33 CDT | 4006b120 | previous session (needs FHSPB16e4k)
    F31 | 2026-10-06 20:33 CDT | 4006b120 | previous session (needs FHSPB16e4k)
    F20 | 2026-10-07 03:23 CDT | f290661f | needs FHU28B16e4 (accepted 10-07 03:01 CDT); figure script ran 03:22-03:23 CDT during the run (1 process, 71 s)
    F24 | 2026-10-07 12:38 CDT | a50d9a37 | needs the 6 rotation rows (last accepted 10-07 12:30 CDT); paper_f24.py ran 12:31:56-12:38:31 CDT during the run (1 process; also rewrites F25, F26)
    F22 | 2026-10-07 13:28 CDT | 3feb07f6 | needs 12 rows (last, FHNR16B16e4, accepted 10-07 13:08 CDT); paper_f22.py ran 13:22:24-13:27:21 CDT during the run (1 process)
    F21 | 2026-10-07 16:15 CDT | adb8a752 | needs all 24 rows (FIGHS_DONE 10-07 16:12 CDT); paper_f21.py ran 16:13:45-16:15:19 CDT (after the run)

**행별 실행·수용** (runner 분 = `logs/run_D2_<TAG>.log` 의 `finished in`; 수용 = 마지막 시작 뒤의 `acceptance` 줄; 추정 = §1b)

| # | TAG | runner 구간 (머리 줄 시각 CDT · resume · done 청크 · exists 청크 · 분) | 수용 (마지막 시작 뒤) | `<TAG>_accept.txt` | raised 시행 | §1b 추정 (min) |
|---|---|---|---|---|---|---|
| 1 | FHSPB16e4k | 2026-10-06 19:38 · r0 · 2048 · 0 · 49.6; 2026-10-06 21:16 · r1 · 0 · 2048 · 0.0 | 10-06 21:17 rc=0 | ACCEPT: OK -- FHSPB16e4k / ACCEPT (f): OK | 0 | 45 |
| 2 | FHPILB16e4k | 2026-10-06 20:29 · r0 · 2048 · 0 · 4.7; 2026-10-06 21:17 · r1 · 0 · 2048 · 0.1 | 10-06 21:18 rc=0 | ACCEPT: OK -- FHPILB16e4k / ACCEPT (f): OK | 0 | 6 |
| 3 | FHB16e4k | 2026-10-06 20:34 · r0 · 2048 · 0 · 1.8; 2026-10-06 21:18 · r1 · 0 · 2048 · 0.0 | 10-06 21:19 rc=0 | ACCEPT: OK -- FHB16e4k / ACCEPT (f): OK | 0 | ≤ 6 |
| 4 | FHD3B16e4 | 2026-10-06 20:37 · r0 · 0 · 0 · 미완; 2026-10-06 21:19 · r1 · 2048 · 0 · 72.5 | 10-06 22:32 rc=0 | ACCEPT: OK -- FHD3B16e4 / ACCEPT (f): OK | 0 | ≤ 85 |
| 5 | FHSPD3 | 2026-10-06 22:32 · r1 · 2048 · 0 · 49.5 | 10-06 23:22 rc=0 | ACCEPT: OK -- FHSPD3 / ACCEPT (f): OK | 0 | 45 |
| 6 | FHPILD3 | 2026-10-06 23:22 · r1 · 2048 · 0 · 7.2 | 10-06 23:30 rc=0 | ACCEPT: OK -- FHPILD3 / ACCEPT (f): OK | 0 | 16 |
| 7 | FHSVB16e4 | 2026-10-06 23:30 · r1 · 2048 · 0 · 34.6 | 10-07 00:05 rc=0 | ACCEPT: OK -- FHSVB16e4 / ACCEPT (f): OK | 0 | ≤ 37 |
| 8 | FHSPSV | 2026-10-07 00:05 · r1 · 2048 · 0 · 30.5 | 10-07 00:36 rc=0 | ACCEPT: OK -- FHSPSV / ACCEPT (f): OK | 0 | 28 |
| 9 | FHPILSV | 2026-10-07 00:37 · r1 · 2048 · 0 · 4.7 | 10-07 00:42 rc=0 | ACCEPT: OK -- FHPILSV / ACCEPT (f): OK | 0 | 13 |
| 10 | FHU28B16e4 | 2026-10-07 00:42 · r1 · 2048 · 0 · 138.9 | 10-07 03:01 rc=0 | ACCEPT: OK -- FHU28B16e4 / ACCEPT (f): OK | 0 | ≤ 129 |
| 11 | FHSPU28 | 2026-10-07 03:01 · r1 · 2048 · 0 · 83.0 | 10-07 04:25 rc=0 | ACCEPT: OK -- FHSPU28 / ACCEPT (f): OK | 0 | 54 |
| 12 | FHPILU28 | 2026-10-07 04:25 · r1 · 2048 · 0 · 75.6 | 10-07 05:42 rc=0 | ACCEPT: OK -- FHPILU28 / ACCEPT (f): OK | 0 | 65 |
| 13 | FHMXB16e4 | 2026-10-07 05:42 · r1 · 2048 · 0 · 137.6 | 10-07 08:00 rc=0 | ACCEPT: OK -- FHMXB16e4 / ACCEPT (f): OK | 0 | ≤ 126 |
| 14 | FHSPMX | 2026-10-07 08:00 · r1 · 2048 · 0 · 93.6 | 10-07 09:34 rc=0 | ACCEPT: OK -- FHSPMX / ACCEPT (f): OK | 0 | 63 |
| 15 | FHPILMX | 2026-10-07 09:34 · r1 · 2048 · 0 · 71.5 | 10-07 10:47 rc=0 | ACCEPT: OK -- FHPILMX / ACCEPT (f): OK | 0 | 61 |
| 16 | FHROTaB16e4k | 2026-10-07 10:47 · r1 · 2048 · 0 · 40.0 | 10-07 11:27 rc=0 | ACCEPT: OK -- FHROTaB16e4k / ACCEPT (f): OK | 0 | 43 |
| 17 | FHXPROTaB16e4k | 2026-10-07 11:27 · r1 · 2048 · 0 · 3.9 | 10-07 11:32 rc=0 | ACCEPT: OK -- FHXPROTaB16e4k / ACCEPT (f): OK | 0 | 6 |
| 18 | FHXAROTaB16e4k | 2026-10-07 11:36 · r1 · 2048 · 0 · 1.9 | 10-07 11:38 rc=0 | ACCEPT: OK -- FHXAROTaB16e4k / ACCEPT (f): OK | 0 | 2 |
| 19 | FHROTbB16e4k | 2026-10-07 11:38 · r1 · 2048 · 0 · 40.2 | 10-07 12:19 rc=0 | ACCEPT: OK -- FHROTbB16e4k / ACCEPT (f): OK | 0 | 43 |
| 20 | FHXPROTbB16e4k | 2026-10-07 12:19 · r1 · 2048 · 0 · 3.9 | 10-07 12:24 rc=0 | ACCEPT: OK -- FHXPROTbB16e4k / ACCEPT (f): OK | 0 | 6 |
| 21 | FHXAROTbB16e4k | 2026-10-07 12:28 · r1 · 2048 · 0 · 1.9 | 10-07 12:30 rc=0 | ACCEPT: OK -- FHXAROTbB16e4k / ACCEPT (f): OK | 0 | 2 |
| 22 | FHPILNR16 | 2026-10-07 12:30 · r1 · 2048 · 0 · 32.8 | 10-07 13:04 rc=0 | ACCEPT: OK -- FHPILNR16 / ACCEPT (f): OK | 0 | 31 |
| 23 | FHNR16B16e4 | 2026-10-07 13:04 · r1 · 2048 · 0 · 3.5 | 10-07 13:08 rc=0 | ACCEPT: OK -- FHNR16B16e4 / ACCEPT (f): OK | 0 | ≤ 56 |
| 24 | FHSPNR16 | 2026-10-07 13:09 · r1 · 2048 · 0 · 183.0 | 10-07 16:12 rc=0 | ACCEPT: OK -- FHSPNR16 / ACCEPT (f): OK | 0 | 168 |

**대조 (phase C; 마지막 시작에서 다시 만든 판정 파일)**

| 대조 태그 | 판정 파일 첫 줄 | 판정 |
|---|---|---|
| FHCSPB16e4k (control) | control raw_FHCSPB16e4k vs ['raw_SPB16e4k']: 4 chunk files (expected 4), arms ['SBL-loop', 'SBL-pilot', 'OMP-pilot', 'R5-genie'], 112 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCPILB16e4k (control) | control raw_FHCPILB16e4k vs ['raw_PILB16e4k']: 4 chunk files (expected 4), arms ['V1-pilot', 'bstar-pilot', 'R5-genie'], 84 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCB16e4k (control) | control raw_FHCB16e4k vs ['raw_B16e4k']: 4 chunk files (expected 4), arms ['R0-pilot', 'R5-genie'], 56 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCD3B16e4 (control) | control raw_FHCD3B16e4 vs ['raw_D3B16e4']: 4 chunk files (expected 4), arms ['R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'M-ours-bstar', 'M-ours-dscore-C-V1', 'R5-genie'], 196 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCSPD3 (control) | control raw_FHCSPD3 vs ['raw_SPD3']: 4 chunk files (expected 4), arms ['SBL-loop', 'SBL-pilot', 'OMP-pilot', 'R5-genie'], 112 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCPILD3 (control) | control raw_FHCPILD3 vs ['raw_PILD3']: 4 chunk files (expected 4), arms ['V1-pilot', 'bstar-pilot', 'R5-genie'], 84 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCSVB16e4 (control) | control raw_FHCSVB16e4 vs ['raw_SVB16e4']: 4 chunk files (expected 4), arms ['R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'M-ours-bstar', 'M-ours-dscore-C-V1', 'R5-genie'], 196 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCSPSV (control) | control raw_FHCSPSV vs ['raw_SPSV']: 4 chunk files (expected 4), arms ['SBL-loop', 'SBL-pilot', 'OMP-pilot', 'R5-genie'], 112 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCPILSV (control) | control raw_FHCPILSV vs ['raw_PILSV']: 4 chunk files (expected 4), arms ['V1-pilot', 'bstar-pilot', 'R5-genie'], 84 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCU28B16e4 (control) | control raw_FHCU28B16e4 vs ['raw_U28B16e4']: 4 chunk files (expected 4), arms ['R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'M-ours-bstar', 'M-ours-dscore-C-V1', 'R5-genie'], 196 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCSPU28 (control) | control raw_FHCSPU28 vs ['raw_SPU28']: 4 chunk files (expected 4), arms ['SBL-loop', 'SBL-pilot', 'OMP-pilot', 'R5-genie'], 112 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCPILU28 (control) | control raw_FHCPILU28 vs ['raw_PILU28']: 4 chunk files (expected 4), arms ['V1-pilot', 'bstar-pilot', 'R5-genie'], 84 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCMXB16e4 (control) | control raw_FHCMXB16e4 vs ['raw_MXB16e4']: 4 chunk files (expected 4), arms ['R0-pilot', 'R1-turbo', 'R2-ours-G', 'R3-bigamp', 'M-ours-bstar', 'M-ours-dscore-C-V1', 'R5-genie'], 196 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCSPMX (control) | control raw_FHCSPMX vs ['raw_SPMX']: 4 chunk files (expected 4), arms ['SBL-loop', 'SBL-pilot', 'OMP-pilot', 'R5-genie'], 112 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCPILMX (control) | control raw_FHCPILMX vs ['raw_PILMX']: 4 chunk files (expected 4), arms ['V1-pilot', 'bstar-pilot', 'R5-genie'], 84 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCROTaB16e4k (control) | control raw_FHCROTaB16e4k vs ['raw_ROTaB16e4k', 'raw_XLROTaB16e4k']: 4 chunk files (expected 4), arms ['M-ours-dscore-C-V1', 'M-ours-bstar', 'R2-ours-G', 'R1-turbo', 'R3-bigamp', 'R5-genie'], 168 (chunk, arm, key) comparisons, 0 d | CONTROL: OK |
| FHCXPROTaB16e4k (control) | control raw_FHCXPROTaB16e4k vs ['raw_XPROTaB16e4k']: 4 chunk files (expected 4), arms ['V1-pilot', 'R5-genie'], 56 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCXAROTaB16e4k (control) | control raw_FHCXAROTaB16e4k vs ['raw_XAROTaB16e4k']: 4 chunk files (expected 4), arms ['ALD-pilot', 'R5-genie'], 56 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCXAROTaB16e4k (aldcontrol) | ALD estimator control results/ald/ald_FHCXAROTaB16e4k.npz vs results/ald/ald_XAROTaB16e4k.npz: hhat (7, 2560, 32), keys hhat b v, max\|diff\| 0, differing none | CONTROL-ALD: OK |
| FHCROTbB16e4k (control) | control raw_FHCROTbB16e4k vs ['raw_ROTbB16e4k', 'raw_XLROTbB16e4k']: 4 chunk files (expected 4), arms ['M-ours-dscore-C-V1', 'M-ours-bstar', 'R2-ours-G', 'R1-turbo', 'R3-bigamp', 'R5-genie'], 168 (chunk, arm, key) comparisons, 0 d | CONTROL: OK |
| FHCXPROTbB16e4k (control) | control raw_FHCXPROTbB16e4k vs ['raw_XPROTbB16e4k']: 4 chunk files (expected 4), arms ['V1-pilot', 'R5-genie'], 56 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCXAROTbB16e4k (control) | control raw_FHCXAROTbB16e4k vs ['raw_XAROTbB16e4k']: 4 chunk files (expected 4), arms ['ALD-pilot', 'R5-genie'], 56 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCXAROTbB16e4k (aldcontrol) | ALD estimator control results/ald/ald_FHCXAROTbB16e4k.npz vs results/ald/ald_XAROTbB16e4k.npz: hhat (7, 2560, 32), keys hhat b v, max\|diff\| 0, differing none | CONTROL-ALD: OK |
| FHCPILNR16 (control) | control raw_FHCPILNR16 vs ['raw_PILNR16']: 4 chunk files (expected 4), arms ['V1-pilot', 'bstar-pilot', 'R5-genie'], 84 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCNR16B16e4 (control) | control raw_FHCNR16B16e4 vs ['raw_NR16B16e4']: 4 chunk files (expected 4), arms ['R0-pilot', 'R5-genie'], 56 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |
| FHCSPNR16 (control) | control raw_FHCSPNR16 vs ['raw_SPNR16']: 4 chunk files (expected 4), arms ['SBL-loop', 'SBL-pilot', 'OMP-pilot', 'R5-genie'], 112 (chunk, arm, key) comparisons, 0 differ | CONTROL: OK |

**매니페스트 요지** (`run_manifest_<TAG>.json`)

| TAG | git | n_raw_files | config_hash | 적합 링크 → 대상 | ckpt sha256[:16] · id | skip_min..skip_max_end | arms | host · 작성 |
|---|---|---|---|---|---|---|---|---|
| FHSPB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHSPB16e4k` → `gmm_fits_D2_B16e4k` | — · (none) | 10000..30480 | OMP-pilot, R5-genie, SBL-loop, SBL-pilot | 262d04c812cc · 2026-10-07 11:16:35 KST |
| FHPILB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHPILB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | R5-genie, V1-pilot, bstar-pilot | 262d04c812cc · 2026-10-07 11:17:36 KST |
| FHB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | R0-pilot, R5-genie | 262d04c812cc · 2026-10-07 11:18:35 KST |
| FHD3B16e4 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHD3B16e4` → `gmm_fits_D2_D3B16e4` | 7ebf4e6647d4413f · sha256[:16]=7ebf4e6647d4413f epoch=494 best_epoch=494 role=best 8x4 | 10000..30480 | M-ours-bstar, M-ours-dscore-C-V1, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R5-genie | 262d04c812cc · 2026-10-07 12:31:58 KST |
| FHSPD3 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHSPD3` → `gmm_fits_D2_D3B16e4` | — · (none) | 10000..30480 | OMP-pilot, R5-genie, SBL-loop, SBL-pilot | 262d04c812cc · 2026-10-07 13:21:46 KST |
| FHPILD3 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHPILD3` → `gmm_fits_D2_D3B16e4` | 7ebf4e6647d4413f · sha256[:16]=7ebf4e6647d4413f epoch=494 best_epoch=494 role=best 8x4 | 10000..30480 | R5-genie, V1-pilot, bstar-pilot | 262d04c812cc · 2026-10-07 13:29:59 KST |
| FHSVB16e4 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHSVB16e4` → `gmm_fits_D2_SVB16e4` | d2d78962c2846364 · sha256[:16]=d2d78962c2846364 epoch=240 best_epoch=240 role=best 8x4 | 10000..30480 | M-ours-bstar, M-ours-dscore-C-V1, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R5-genie | 262d04c812cc · 2026-10-07 14:05:29 KST |
| FHSPSV | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHSPSV` → `gmm_fits_D2_SVB16e4` | — · (none) | 10000..30480 | OMP-pilot, R5-genie, SBL-loop, SBL-pilot | 262d04c812cc · 2026-10-07 14:36:17 KST |
| FHPILSV | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHPILSV` → `gmm_fits_D2_SVB16e4` | d2d78962c2846364 · sha256[:16]=d2d78962c2846364 epoch=240 best_epoch=240 role=best 8x4 | 10000..30480 | R5-genie, V1-pilot, bstar-pilot | 262d04c812cc · 2026-10-07 14:41:58 KST |
| FHU28B16e4 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHU28B16e4` → `gmm_fits_D2_U28B16e4` | 6f3a1b9490864af1 · sha256[:16]=6f3a1b9490864af1 epoch=379 best_epoch=379 role=best 8x4 | 10000..30480 | M-ours-bstar, M-ours-dscore-C-V1, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R5-genie | 262d04c812cc · 2026-10-07 17:01:48 KST |
| FHSPU28 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHSPU28` → `gmm_fits_D2_U28B16e4` | — · (none) | 10000..30480 | OMP-pilot, R5-genie, SBL-loop, SBL-pilot | 262d04c812cc · 2026-10-07 18:25:04 KST |
| FHPILU28 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHPILU28` → `gmm_fits_D2_U28B16e4` | 6f3a1b9490864af1 · sha256[:16]=6f3a1b9490864af1 epoch=379 best_epoch=379 role=best 8x4 | 10000..30480 | R5-genie, V1-pilot, bstar-pilot | 262d04c812cc · 2026-10-07 19:41:36 KST |
| FHMXB16e4 | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHMXB16e4` → `gmm_fits_D2_MXB16e4` | b591ae24ae3c5f31 · sha256[:16]=b591ae24ae3c5f31 epoch=464 best_epoch=464 role=best 8x4 | 10000..30480 | M-ours-bstar, M-ours-dscore-C-V1, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R5-genie | 262d04c812cc · 2026-10-07 22:00:06 KST |
| FHSPMX | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHSPMX` → `gmm_fits_D2_MXB16e4` | — · (none) | 10000..30480 | OMP-pilot, R5-genie, SBL-loop, SBL-pilot | 262d04c812cc · 2026-10-07 23:34:02 KST |
| FHPILMX | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHPILMX` → `gmm_fits_D2_MXB16e4` | b591ae24ae3c5f31 · sha256[:16]=b591ae24ae3c5f31 epoch=464 best_epoch=464 role=best 8x4 | 10000..30480 | R5-genie, V1-pilot, bstar-pilot | 262d04c812cc · 2026-10-08 00:46:28 KST |
| FHROTaB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHROTaB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | M-ours-bstar, M-ours-dscore-C-V1, R1-turbo, R2-ours-G, R3-bigamp, R5-genie | 262d04c812cc · 2026-10-08 01:27:24 KST |
| FHXPROTaB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHXPROTaB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | R5-genie, V1-pilot | 262d04c812cc · 2026-10-08 01:31:35 KST |
| FHXAROTaB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHXAROTaB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | ALD-pilot, R5-genie | 262d04c812cc · 2026-10-08 01:38:11 KST |
| FHROTbB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHROTbB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | M-ours-bstar, M-ours-dscore-C-V1, R1-turbo, R2-ours-G, R3-bigamp, R5-genie | 262d04c812cc · 2026-10-08 02:19:21 KST |
| FHXPROTbB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHXPROTbB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | R5-genie, V1-pilot | 262d04c812cc · 2026-10-08 02:23:33 KST |
| FHXAROTbB16e4k | 331f6e57 | 2048 | b9c95a599873d719 | `gmm_fits_D2_FHXAROTbB16e4k` → `gmm_fits_D2_B16e4k` | 4443921ce8d5c4a1 · sha256[:16]=4443921ce8d5c4a1 epoch=1784 best_epoch=1764 role=legacy-last 8x4 \| BEST_WEIGHTS_UNAVAILABLE: evaluated = last-epoch EMA, reported best_val belongs to best_epoch | 10000..30480 | ALD-pilot, R5-genie | 262d04c812cc · 2026-10-08 02:30:10 KST |
| FHPILNR16 | 331f6e57 | 2048 | 3dc8b2cac46aec74 | `gmm_fits_D2_FHPILNR16` → `gmm_fits_D2_NR16B16e4` | c050d611b2c714a6 · sha256[:16]=c050d611b2c714a6 epoch=1684 best_epoch=1684 role=best 16x4 | 10000..30480 | R5-genie, V1-pilot, bstar-pilot | 262d04c812cc · 2026-10-08 03:03:51 KST |
| FHNR16B16e4 | 331f6e57 | 2048 | 3dc8b2cac46aec74 | `gmm_fits_D2_FHNR16B16e4` → `gmm_fits_D2_NR16B16e4` | c050d611b2c714a6 · sha256[:16]=c050d611b2c714a6 epoch=1684 best_epoch=1684 role=best 16x4 | 10000..30480 | R0-pilot, R5-genie | 262d04c812cc · 2026-10-08 03:08:16 KST |
| FHSPNR16 | 331f6e57 | 2048 | 3dc8b2cac46aec74 | `gmm_fits_D2_FHSPNR16` → `gmm_fits_D2_NR16B16e4` | — · (none) | 10000..30480 | OMP-pilot, R5-genie, SBL-loop, SBL-pilot | 262d04c812cc · 2026-10-08 06:12:07 KST |

**보고 표 (전부 보고 전용 — 판정 아님; `fighs_<TAG>.txt` 의 실패 / 20480 · BLER; 95% Wilson 은 그 파일에)** — 반복 16

**D2 C2 (Sparse specular 8×4)**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| OMP-pilot (FHSPB16e4k) | 618 · 3.02e-02 | 472 · 2.30e-02 | 368 · 1.80e-02 | 298 · 1.46e-02 |
| SBL-loop (FHSPB16e4k) | 363 · 1.77e-02 | 204 · 9.96e-03 | 116 · 5.66e-03 | 87 · 4.25e-03 |
| SBL-pilot (FHSPB16e4k) | 378 · 1.85e-02 | 204 · 9.96e-03 | 140 · 6.84e-03 | 88 · 4.30e-03 |
| V1-pilot (FHPILB16e4k) | 119 · 5.81e-03 | 62 · 3.03e-03 | 33 · 1.61e-03 | 27 · 1.32e-03 |
| bstar-pilot (FHPILB16e4k) | 254 · 1.24e-02 | 152 · 7.42e-03 | 92 · 4.49e-03 | 82 · 4.00e-03 |
| R0-pilot (FHB16e4k) | 518 · 2.53e-02 | 311 · 1.52e-02 | 203 · 9.91e-03 | 137 · 6.69e-03 |
| R0-pilot@1 (FHB16e4k) | 2216 · 1.08e-01 | 1379 · 6.73e-02 | 951 · 4.64e-02 | 715 · 3.49e-02 |
| R5-genie (FHSPB16e4k, FHPILB16e4k, FHB16e4k: 같은 수) | 66 · 3.22e-03 | 36 · 1.76e-03 | 16 · 7.81e-04 | 13 · 6.35e-04 |

**D3 (S2c) C2**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-bstar (FHD3B16e4) | 788 · 3.85e-02 | 429 · 2.09e-02 | 225 · 1.10e-02 | 142 · 6.93e-03 |
| M-ours-dscore-C-V1 (FHD3B16e4) | 399 · 1.95e-02 | 182 · 8.89e-03 | 101 · 4.93e-03 | 55 · 2.69e-03 |
| R0-pilot (FHD3B16e4) | 1449 · 7.08e-02 | 796 · 3.89e-02 | 464 · 2.27e-02 | 272 · 1.33e-02 |
| R0-pilot@1 (FHD3B16e4) | 4477 · 2.19e-01 | 2636 · 1.29e-01 | 1730 · 8.45e-02 | 1115 · 5.44e-02 |
| R1-turbo (FHD3B16e4) | 2148 · 1.05e-01 | 1164 · 5.68e-02 | 678 · 3.31e-02 | 380 · 1.86e-02 |
| R2-ours-G (FHD3B16e4) | 1237 · 6.04e-02 | 750 · 3.66e-02 | 436 · 2.13e-02 | 234 · 1.14e-02 |
| R3-bigamp (FHD3B16e4) | 2991 · 1.46e-01 | 2656 · 1.30e-01 | 2882 · 1.41e-01 | 2720 · 1.33e-01 |
| OMP-pilot (FHSPD3) | 1627 · 7.94e-02 | 1081 · 5.28e-02 | 645 · 3.15e-02 | 450 · 2.20e-02 |
| SBL-loop (FHSPD3) | 1028 · 5.02e-02 | 500 · 2.44e-02 | 332 · 1.62e-02 | 167 · 8.15e-03 |
| SBL-pilot (FHSPD3) | 1084 · 5.29e-02 | 551 · 2.69e-02 | 349 · 1.70e-02 | 164 · 8.01e-03 |
| V1-pilot (FHPILD3) | 481 · 2.35e-02 | 201 · 9.81e-03 | 116 · 5.66e-03 | 57 · 2.78e-03 |
| bstar-pilot (FHPILD3) | 919 · 4.49e-02 | 474 · 2.31e-02 | 248 · 1.21e-02 | 155 · 7.57e-03 |
| R5-genie (FHD3B16e4, FHSPD3, FHPILD3: 같은 수) | 182 · 8.89e-03 | 107 · 5.22e-03 | 57 · 2.78e-03 | 26 · 1.27e-03 |

**SV8e C2**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-bstar (FHSVB16e4) | 10 · 4.88e-04 | 3 · 1.46e-04 | 0 · 0.00e+00 | 0 · 0.00e+00 |
| M-ours-dscore-C-V1 (FHSVB16e4) | 2 · 9.77e-05 | 1 · 4.88e-05 | 1 · 4.88e-05 | 0 · 0.00e+00 |
| R0-pilot (FHSVB16e4) | 28 · 1.37e-03 | 11 · 5.37e-04 | 1 · 4.88e-05 | 0 · 0.00e+00 |
| R0-pilot@1 (FHSVB16e4) | 250 · 1.22e-02 | 69 · 3.37e-03 | 17 · 8.30e-04 | 6 · 2.93e-04 |
| R1-turbo (FHSVB16e4) | 58 · 2.83e-03 | 22 · 1.07e-03 | 2 · 9.77e-05 | 0 · 0.00e+00 |
| R2-ours-G (FHSVB16e4) | 14 · 6.84e-04 | 6 · 2.93e-04 | 0 · 0.00e+00 | 0 · 0.00e+00 |
| R3-bigamp (FHSVB16e4) | 181 · 8.84e-03 | 155 · 7.57e-03 | 120 · 5.86e-03 | 132 · 6.45e-03 |
| OMP-pilot (FHSPSV) | 85 · 4.15e-03 | 17 · 8.30e-04 | 3 · 1.46e-04 | 1 · 4.88e-05 |
| SBL-loop (FHSPSV) | 14 · 6.84e-04 | 5 · 2.44e-04 | 0 · 0.00e+00 | 0 · 0.00e+00 |
| SBL-pilot (FHSPSV) | 12 · 5.86e-04 | 5 · 2.44e-04 | 0 · 0.00e+00 | 0 · 0.00e+00 |
| V1-pilot (FHPILSV) | 8 · 3.91e-04 | 3 · 1.46e-04 | 0 · 0.00e+00 | 0 · 0.00e+00 |
| bstar-pilot (FHPILSV) | 3 · 1.46e-04 | 2 · 9.77e-05 | 0 · 0.00e+00 | 0 · 0.00e+00 |
| R5-genie (FHSVB16e4, FHSPSV, FHPILSV: 같은 수) | 1 · 4.88e-05 | 0 · 0.00e+00 | 0 · 0.00e+00 | 0 · 0.00e+00 |

**UMi28 C2**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-bstar (FHU28B16e4) | 2029 · 9.91e-02 | 1079 · 5.27e-02 | 546 · 2.67e-02 | 223 · 1.09e-02 |
| M-ours-dscore-C-V1 (FHU28B16e4) | 1746 · 8.53e-02 | 866 · 4.23e-02 | 386 · 1.88e-02 | 145 · 7.08e-03 |
| R0-pilot (FHU28B16e4) | 3066 · 1.50e-01 | 1660 · 8.11e-02 | 810 · 3.96e-02 | 351 · 1.71e-02 |
| R0-pilot@1 (FHU28B16e4) | 5569 · 2.72e-01 | 3534 · 1.73e-01 | 2077 · 1.01e-01 | 1039 · 5.07e-02 |
| R1-turbo (FHU28B16e4) | 3585 · 1.75e-01 | 1911 · 9.33e-02 | 949 · 4.63e-02 | 392 · 1.91e-02 |
| R2-ours-G (FHU28B16e4) | 2798 · 1.37e-01 | 1529 · 7.47e-02 | 769 · 3.75e-02 | 323 · 1.58e-02 |
| R3-bigamp (FHU28B16e4) | 6021 · 2.94e-01 | 5791 · 2.83e-01 | 6126 · 2.99e-01 | 6030 · 2.94e-01 |
| OMP-pilot (FHSPU28) | 4006 · 1.96e-01 | 2290 · 1.12e-01 | 1186 · 5.79e-02 | 550 · 2.69e-02 |
| SBL-loop (FHSPU28) | 2392 · 1.17e-01 | 1293 · 6.31e-02 | 627 · 3.06e-02 | 236 · 1.15e-02 |
| SBL-pilot (FHSPU28) | 2576 · 1.26e-01 | 1408 · 6.88e-02 | 669 · 3.27e-02 | 268 · 1.31e-02 |
| V1-pilot (FHPILU28) | 1937 · 9.46e-02 | 961 · 4.69e-02 | 419 · 2.05e-02 | 157 · 7.67e-03 |
| bstar-pilot (FHPILU28) | 2233 · 1.09e-01 | 1187 · 5.80e-02 | 592 · 2.89e-02 | 229 · 1.12e-02 |
| R5-genie (FHU28B16e4, FHSPU28, FHPILU28: 같은 수) | 525 · 2.56e-02 | 216 · 1.05e-02 | 81 · 3.96e-03 | 23 · 1.12e-03 |

**MIX3 C2**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-bstar (FHMXB16e4) | 1840 · 8.98e-02 | 963 · 4.70e-02 | 444 · 2.17e-02 | 225 · 1.10e-02 |
| M-ours-dscore-C-V1 (FHMXB16e4) | 1499 · 7.32e-02 | 702 · 3.43e-02 | 313 · 1.53e-02 | 141 · 6.88e-03 |
| R0-pilot (FHMXB16e4) | 3187 · 1.56e-01 | 1768 · 8.63e-02 | 948 · 4.63e-02 | 451 · 2.20e-02 |
| R0-pilot@1 (FHMXB16e4) | 7048 · 3.44e-01 | 4735 · 2.31e-01 | 3116 · 1.52e-01 | 1875 · 9.16e-02 |
| R1-turbo (FHMXB16e4) | 4063 · 1.98e-01 | 2233 · 1.09e-01 | 1220 · 5.96e-02 | 568 · 2.77e-02 |
| R2-ours-G (FHMXB16e4) | 2876 · 1.40e-01 | 1603 · 7.83e-02 | 855 · 4.17e-02 | 428 · 2.09e-02 |
| R3-bigamp (FHMXB16e4) | 6258 · 3.06e-01 | 5952 · 2.91e-01 | 6266 · 3.06e-01 | 6284 · 3.07e-01 |
| OMP-pilot (FHSPMX) | 4606 · 2.25e-01 | 2693 · 1.31e-01 | 1555 · 7.59e-02 | 828 · 4.04e-02 |
| SBL-loop (FHSPMX) | 2480 · 1.21e-01 | 1265 · 6.18e-02 | 655 · 3.20e-02 | 320 · 1.56e-02 |
| SBL-pilot (FHSPMX) | 2691 · 1.31e-01 | 1420 · 6.93e-02 | 723 · 3.53e-02 | 334 · 1.63e-02 |
| V1-pilot (FHPILMX) | 1672 · 8.16e-02 | 794 · 3.88e-02 | 328 · 1.60e-02 | 147 · 7.18e-03 |
| bstar-pilot (FHPILMX) | 2045 · 9.99e-02 | 1045 · 5.10e-02 | 499 · 2.44e-02 | 243 · 1.19e-02 |
| R5-genie (FHMXB16e4, FHSPMX, FHPILMX: 같은 수) | 482 · 2.35e-02 | 184 · 8.98e-03 | 73 · 3.56e-03 | 42 · 2.05e-03 |

**D2 C2 회전 15°**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-bstar (FHROTaB16e4k) | 293 · 1.43e-02 | 147 · 7.18e-03 | 107 · 5.22e-03 | 78 · 3.81e-03 |
| M-ours-dscore-C-V1 (FHROTaB16e4k) | 141 · 6.88e-03 | 66 · 3.22e-03 | 42 · 2.05e-03 | 24 · 1.17e-03 |
| R1-turbo (FHROTaB16e4k) | 948 · 4.63e-02 | 539 · 2.63e-02 | 295 · 1.44e-02 | 198 · 9.67e-03 |
| R2-ours-G (FHROTaB16e4k) | 520 · 2.54e-02 | 306 · 1.49e-02 | 178 · 8.69e-03 | 136 · 6.64e-03 |
| R3-bigamp (FHROTaB16e4k) | 1159 · 5.66e-02 | 1047 · 5.11e-02 | 1205 · 5.88e-02 | 1146 · 5.60e-02 |
| V1-pilot (FHXPROTaB16e4k) | 148 · 7.23e-03 | 70 · 3.42e-03 | 43 · 2.10e-03 | 20 · 9.77e-04 |
| ALD-pilot (FHXAROTaB16e4k) | 330 · 1.61e-02 | 135 · 6.59e-03 | 78 · 3.81e-03 | 71 · 3.47e-03 |
| R5-genie (FHROTaB16e4k, FHXPROTaB16e4k, FHXAROTaB16e4k: 같은 수) | 71 · 3.47e-03 | 36 · 1.76e-03 | 19 · 9.28e-04 | 18 · 8.79e-04 |

**D2 C2 회전 30°**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| M-ours-bstar (FHROTbB16e4k) | 385 · 1.88e-02 | 246 · 1.20e-02 | 159 · 7.76e-03 | 104 · 5.08e-03 |
| M-ours-dscore-C-V1 (FHROTbB16e4k) | 175 · 8.54e-03 | 107 · 5.22e-03 | 62 · 3.03e-03 | 39 · 1.90e-03 |
| R1-turbo (FHROTbB16e4k) | 1143 · 5.58e-02 | 654 · 3.19e-02 | 383 · 1.87e-02 | 227 · 1.11e-02 |
| R2-ours-G (FHROTbB16e4k) | 612 · 2.99e-02 | 378 · 1.85e-02 | 222 · 1.08e-02 | 153 · 7.47e-03 |
| R3-bigamp (FHROTbB16e4k) | 1362 · 6.65e-02 | 1299 · 6.34e-02 | 1418 · 6.92e-02 | 1397 · 6.82e-02 |
| V1-pilot (FHXPROTbB16e4k) | 197 · 9.62e-03 | 110 · 5.37e-03 | 63 · 3.08e-03 | 42 · 2.05e-03 |
| ALD-pilot (FHXAROTbB16e4k) | 385 · 1.88e-02 | 208 · 1.02e-02 | 112 · 5.47e-03 | 106 · 5.18e-03 |
| R5-genie (FHROTbB16e4k, FHXPROTbB16e4k, FHXAROTbB16e4k: 같은 수) | 79 · 3.86e-03 | 43 · 2.10e-03 | 31 · 1.51e-03 | 14 · 6.84e-04 |

**D2 C6 (Sparse specular 16×4)**

| arm (TAG) | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|
| V1-pilot (FHPILNR16) | 38 · 1.86e-03 | 32 · 1.56e-03 | 28 · 1.37e-03 | 21 · 1.03e-03 |
| bstar-pilot (FHPILNR16) | 202 · 9.86e-03 | 144 · 7.03e-03 | 88 · 4.30e-03 | 57 · 2.78e-03 |
| R0-pilot (FHNR16B16e4) | 341 · 1.67e-02 | 240 · 1.17e-02 | 142 · 6.93e-03 | 85 · 4.15e-03 |
| R0-pilot@1 (FHNR16B16e4) | 1179 · 5.76e-02 | 867 · 4.23e-02 | 598 · 2.92e-02 | 398 · 1.94e-02 |
| OMP-pilot (FHSPNR16) | 390 · 1.90e-02 | 282 · 1.38e-02 | 164 · 8.01e-03 | 146 · 7.13e-03 |
| SBL-loop (FHSPNR16) | 251 · 1.23e-02 | 154 · 7.52e-03 | 102 · 4.98e-03 | 62 · 3.03e-03 |
| SBL-pilot (FHSPNR16) | 260 · 1.27e-02 | 174 · 8.50e-03 | 119 · 5.81e-03 | 67 · 3.27e-03 |
| R5-genie (FHPILNR16, FHNR16B16e4, FHSPNR16: 같은 수) | 17 · 8.30e-04 | 16 · 7.81e-04 | 7 · 3.42e-04 | 7 · 3.42e-04 |

집계표 머리말의 `load_raw warnings`: 0 (표 24 개의 값 집합)

**원 raw (n = 2560) 실패 수** — `analysis.load_raw` (경고 수 {'raw_SPB16e4k': 0, 'raw_PILB16e4k': 0, 'raw_B16e4k': 0, 'raw_D3B16e4': 0, 'raw_SPD3': 0, 'raw_PILD3': 0, 'raw_SVB16e4': 0, 'raw_SPSV': 0, 'raw_PILSV': 0, 'raw_U28B16e4': 0, 'raw_SPU28': 0, 'raw_PILU28': 0, 'raw_MXB16e4': 0, 'raw_SPMX': 0, 'raw_PILMX': 0, 'raw_ROTaB16e4k': 0, 'raw_XLROTaB16e4k': 0, 'raw_XPROTaB16e4k': 0, 'raw_XAROTaB16e4k': 0, 'raw_ROTbB16e4k': 0, 'raw_XLROTbB16e4k': 0, 'raw_XPROTbB16e4k': 0, 'raw_XAROTbB16e4k': 0, 'raw_PILNR16': 0, 'raw_NR16B16e4': 0, 'raw_SPNR16': 0}) 로 다시 계산, 반복 16, 비유한 → 실패. 등록 §0.4 와 대조: 곡선 76 개 중 §0.4 에 있는 76 개, 불일치 0 ; 원 raw 의 n: [2560]

**§3 예측 1** — 다시 그리는 곡선 76 개 (실행·수용된 것; 76 개 중) × 4 SNR = 304 칸: 새 점추정 (n = 20480) ∈ 원 raw (n = 2560) 95% Wilson 구간 (닫힌 구간) 281/304 = 0.9243 (기준 ≥ 0.90)

| 묶음 | 곡선 수 | 칸 | 구간 안 |
|---|---|---|---|
| D2 C2 (Sparse specular 8×4) | 6 | 24 | 21 |
| D3 (S2c) C2 | 12 | 48 | 38 |
| SV8e C2 | 12 | 48 | 45 |
| UMi28 C2 | 12 | 48 | 47 |
| MIX3 C2 | 12 | 48 | 44 |
| D2 C2 회전 15° | 8 | 32 | 32 |
| D2 C2 회전 30° | 8 | 32 | 32 |
| D2 C6 (Sparse specular 16×4) | 6 | 24 | 22 |

구간 밖 23 칸 (묶음, arm, SNR, 원 실패 / 2560, 원 95% Wilson, 새 실패 / 20480, 새 BLER):
- D2 C2 (Sparse specular 8×4) · SBL-loop · +12 dB · 27 · [7.26e-03, 1.53e-02] · 116 · 5.66e-03
- D2 C2 (Sparse specular 8×4) · SBL-pilot · +12 dB · 28 · [7.58e-03, 1.58e-02] · 140 · 6.84e-03
- D2 C2 (Sparse specular 8×4) · OMP-pilot · +12 dB · 60 · [1.83e-02, 3.01e-02] · 368 · 1.80e-02
- D3 (S2c) C2 · R0-pilot · +6 dB · 218 · [7.50e-02, 9.66e-02] · 1449 · 7.08e-02
- D3 (S2c) C2 · R2-ours-G · +6 dB · 199 · [6.80e-02, 8.88e-02] · 1237 · 6.04e-02
- D3 (S2c) C2 · R2-ours-G · +9 dB · 75 · [2.34e-02, 3.66e-02] · 750 · 3.66e-02
- D3 (S2c) C2 · R3-bigamp · +9 dB · 294 · [1.03e-01, 1.28e-01] · 2656 · 1.30e-01
- D3 (S2c) C2 · M-ours-dscore-C-V1 · +6 dB · 64 · [1.96e-02, 3.18e-02] · 399 · 1.95e-02
- D3 (S2c) C2 · M-ours-dscore-C-V1 · +12 dB · 22 · [5.68e-03, 1.30e-02] · 101 · 4.93e-03
- D3 (S2c) C2 · R5-genie · +6 dB · 35 · [9.85e-03, 1.90e-02] · 182 · 8.89e-03
- D3 (S2c) C2 · R5-genie · +12 dB · 14 · [3.26e-03, 9.16e-03] · 57 · 2.78e-03
- D3 (S2c) C2 · V1-pilot · +6 dB · 80 · [2.52e-02, 3.87e-02] · 481 · 2.35e-02
- D3 (S2c) C2 · V1-pilot · +12 dB · 25 · [6.62e-03, 1.44e-02] · 116 · 5.66e-03
- SV8e C2 · R1-turbo · +15 dB · 1 · [6.90e-05, 2.21e-03] · 0 · 0.00e+00
- SV8e C2 · R3-bigamp · +15 dB · 26 · [6.94e-03, 1.48e-02] · 132 · 6.45e-03
- SV8e C2 · R5-genie · +6 dB · 1 · [6.90e-05, 2.21e-03] · 1 · 4.88e-05
- UMi28 C2 · SBL-loop · +15 dB · 42 · [1.22e-02, 2.21e-02] · 236 · 1.15e-02
- MIX3 C2 · M-ours-bstar · +15 dB · 16 · [3.85e-03, 1.01e-02] · 225 · 1.10e-02
- MIX3 C2 · R5-genie · +9 dB · 35 · [9.85e-03, 1.90e-02] · 184 · 8.98e-03
- MIX3 C2 · SBL-loop · +9 dB · 183 · [6.21e-02, 8.21e-02] · 1265 · 6.18e-02
- MIX3 C2 · bstar-pilot · +15 dB · 19 · [4.76e-03, 1.16e-02] · 243 · 1.19e-02
- D2 C6 (Sparse specular 16×4) · SBL-loop · +9 dB · 8 · [1.58e-03, 6.15e-03] · 154 · 7.52e-03
- D2 C6 (Sparse specular 16×4) · OMP-pilot · +9 dB · 22 · [5.68e-03, 1.30e-02] · 282 · 1.38e-02

**§3 예측 2 · 오르는 칸** (BLER 이 바로 아래 SNR 점보다 큰 칸; 동률 아님; +3 → +6 dB 칸은 두 시행 집합 비교이며 기록만 — 예측 2 의 분자에 넣지 않는다)

- 원 raw (n = 2560), +6..+15 dB 에 오르는 칸이 있는 곡선: R3 제외 9/70 [('D2 C2 (Sparse specular 8×4)', 'SBL-loop'), ('D2 C2 (Sparse specular 8×4)', 'SBL-pilot'), ('D2 C2 (Sparse specular 8×4)', 'bstar-pilot'), ('D3 (S2c) C2', 'R5-genie'), ('SV8e C2', 'R1-turbo'), ('D2 C2 회전 15°', 'R5-genie'), ('D2 C2 회전 30°', 'R5-genie'), ('D2 C6 (Sparse specular 16×4)', 'V1-pilot'), ('D2 C6 (Sparse specular 16×4)', 'SBL-loop')]; 전체 15/76 (등록 §0.4 의 ↑ 표시 15 개와 일치)
- 새 raw (n = 20480), +6..+15 dB 에 오르는 칸이 있는 곡선: R3 제외 **0/70** [] (예측: 원 raw 의 9 개보다 적다)

| 묶음 | arm | 칸 | 아래 점 (실패 / n) | 위 점 (실패 / n) | 단측 Fisher p (greater) | 예측 2 분자 |
|---|---|---|---|---|---|---|
| D3 (S2c) C2 | R3-bigamp | +9 → +12 dB | 2656 / 20480 | 2882 / 20480 | 0.00057 | R3 제외 |
| SV8e C2 | R3-bigamp | +12 → +15 dB | 120 / 20480 | 132 / 20480 | 0.24 | R3 제외 |
| SV8e C2 | R5-genie | +3 → +6 dB | 0 / 2560 | 1 / 20480 | 0.89 | —  (기록만) |
| UMi28 C2 | R3-bigamp | +9 → +12 dB | 5791 / 20480 | 6126 / 20480 | 0.00014 | R3 제외 |
| MIX3 C2 | R3-bigamp | +9 → +12 dB | 5952 / 20480 | 6266 / 20480 | 0.00036 | R3 제외 |
| MIX3 C2 | R3-bigamp | +12 → +15 dB | 6266 / 20480 | 6284 / 20480 | 0.43 | R3 제외 |
| D2 C2 회전 15° | R3-bigamp | +9 → +12 dB | 1047 / 20480 | 1205 / 20480 | 0.00033 | R3 제외 |
| D2 C2 회전 30° | R3-bigamp | +9 → +12 dB | 1299 / 20480 | 1418 / 20480 | 0.0096 | R3 제외 |

**§3 예측 3** — V1 실패 ≤ b\* 실패 (같은 시행, 동률 포함), D3·SV8e·UMi28·MIX3·회전 15°·30° × 4 SNR

| 묶음 (TAG) | +6 dB V1 : b\* | +9 dB | +12 dB | +15 dB | 성립 칸 |
|---|---|---|---|---|---|
| D3 (S2c) C2 (FHD3B16e4) | 399 : 788 | 182 : 429 | 101 : 225 | 55 : 142 | 4/4 |
| SV8e C2 (FHSVB16e4) | 2 : 10 | 1 : 3 | 1 : 0 | 0 : 0 | 3/4 |
| UMi28 C2 (FHU28B16e4) | 1746 : 2029 | 866 : 1079 | 386 : 546 | 145 : 223 | 4/4 |
| MIX3 C2 (FHMXB16e4) | 1499 : 1840 | 702 : 963 | 313 : 444 | 141 : 225 | 4/4 |
| D2 C2 회전 15° (FHROTaB16e4k) | 141 : 293 | 66 : 147 | 42 : 107 | 24 : 78 | 4/4 |
| D2 C2 회전 30° (FHROTbB16e4k) | 175 : 385 | 107 : 246 | 62 : 159 | 39 : 104 | 4/4 |

합 **23/24** (기준 ≥ 22/24)

**소요** (실행 로그의 분 단위 시각)

- 첫 시작 10-06 19:30; 그 구간의 마지막 시각 줄: `[fighs 10-06 20:37 CDT] FHD3B16e4 run: --testbed D2 --prior S2c --cell`
- 재개 10-06 21:15 → FIGHS_DONE 10-07 16:12: 18.95 h; 첫 구간 10-06 19:30 부터의 벽시계 20.70 h
- runner `finished in` 분의 합 (청크를 계산한 구간만, 0.5 분 미만의 exists-only 구간 제외): 1166.4 min; §1b 합계 추정 ≈ 1151 min

**§3 예측 채점** (보고 전용; 적중/빗나감만; 분모 = 실행·수용된 곡선)

| # | 예측 | 결정하는 수 | 채점 |
|---|---|---|---|
| 1 | 다시 그리는 곡선 × 4 SNR 칸의 ≥ 90 % 에서 새 점추정 ∈ 원 raw 95% Wilson | 281/304 = 0.9243 | ✓ |
| 2 | R3-bigamp 를 뺀 곡선 중 +6 → +9 → +12 → +15 dB 에 오르는 칸이 있는 곡선이 원 raw 의 9 개보다 적다 | 새 raw 0/70 (원 raw 재계산 9/70) | ✓ |
| 3 | V1 실패 ≤ b\* 실패, 24 칸 중 ≥ 22 | 23/24 | ✓ |

합계: 적중 3, 빗나감 0.

**환경 (이 초안을 만들 때 읽은 값)**

- hostname `262d04c812cc`; 컨테이너 PID 1 시작 `화 10월  6 20:38:41 2026` (CDT, `TZ=America/Chicago ps -o lstart= -p 1`); 호스트 uptime `up 1 week, 2 days, 18 hours, 36 minutes`; NVIDIA 드라이버 `580.178.04`; `ldd (Ubuntu GLIBC 2.39-0ubuntu8.7) 2.39`; `/var/log/apt/history.log` 마지막 Start-Date `Start-Date: 2026-07-07  13:42:56`
- 중단 전 매니페스트 (`before/run_manifest_FHB16e4k.json`) 의 versions: `{"python": "3.12.14", "numpy": "2.5.2", "torch": "2.14.0+cu130", "host": "0695aede856d", "cpu_count": 192}`
- 새 시행 ALD 추정 파일: `ald_XAROTaB16e4k_hisnr.npz` sha256[:16] d962c0b6cf7e47a6, mtime 10-08 01:36:09 KST, prov git 331f6e57; `ald_XAROTbB16e4k_hisnr.npz` sha256[:16] bc23a889d2521ec0, mtime 10-08 02:28:07 KST, prov git 331f6e57

**실행 구간 (첫 시작 ~ FIGHS_DONE) 에 주 세션이 돌린 다른 CPU 작업** (세션 기록 `~/.claude/projects/-home-HTJ-t2/<세션>.jsonl` 의 Bash 도구 호출·결과 시각, UTC−5 로 환산; 대상: 그림 스크립트 `paper_f*.py`·`fighs_merge.py`, 이 생성기 `s6_gen.py`, `sync_paper_branch.sh`)

- 세션 6cbef450:
    - fighs_merge, paper_f17: 10-06 19:58:44 – 10-06 20:01:47 CDT
    - sync_paper_branch.sh: 10-06 20:02:05 – 10-06 20:02:11 CDT
    - paper_f16, paper_f31: 10-06 20:29:33 – 10-06 20:32:38 CDT
    - sync_paper_branch.sh: 10-06 20:33:02 – 10-06 20:33:08 CDT
- 세션 8a735dc6:
    - paper_f20: 10-07 03:22:23 – 10-07 03:23:35 CDT
    - sync_paper_branch.sh: 10-07 03:23:44 – 10-07 03:23:52 CDT
    - paper_f24: 10-07 12:31:55 – 10-07 12:38:32 CDT
    - sync_paper_branch.sh: 10-07 12:38:48 – 10-07 12:38:56 CDT
    - paper_f22: 10-07 13:22:22 – 10-07 13:27:22 CDT
    - sync_paper_branch.sh: 10-07 13:28:00 – 10-07 13:28:08 CDT
    - s6_gen: 10-07 13:56:38 – 10-07 13:58:47 CDT

**묶음별 runner 분** (청크를 계산한 구간의 `finished in` 합 대 §1b 추정 합)

| 묶음 | runner 분 | §1b 추정 (min) |
|---|---|---|
| D2 C2 (Sparse specular 8×4) | 56.1 | 57 |
| D3 (S2c) C2 | 129.2 | 146 |
| SV8e C2 | 69.8 | 78 |
| UMi28 C2 | 297.5 | 248 |
| MIX3 C2 | 302.7 | 250 |
| D2 C2 회전 15° | 45.8 | 51 |
| D2 C2 회전 30° | 46.0 | 51 |
| D2 C6 (Sparse specular 16×4) | 219.3 | 255 |

**다시 그린 그림의 기록 텍스트가 적은 오르는 칸** (`conference/figures/records/paper_f<NN>.txt` 의 `rising:` 줄 그대로; HISNR raw 에서 오는 곡선 포함)

- `paper_f16.txt` (10-08 06:16:31 KST, 31 줄): 없음
- `paper_f17.txt` (10-08 06:16:37 KST, 62 줄): 없음
- `paper_f20.txt` (10-08 06:16:15 KST, 23 줄): 없음
- `paper_f21.txt` (10-08 06:17:20 KST, 180 줄): 
    - R3-bigamp @16 1083/20480 1033/20480 1116/20480 1100/20480 (raw_HSB16e4k) rising: +9->+12 dB p=0.035
    - R3-bigamp @16 1090/20480 1265/20480 1418/20480 1099/20480 (raw_HSNR16) rising: +6->+9 dB p=0.00011; +9->+12 dB p=0.0012
    - R3-bigamp @16 2991/20480 2656/20480 2882/20480 2720/20480 (raw_FHD3B16e4) rising: +9->+12 dB p=0.00057
    - R3-bigamp @16 181/20480 155/20480 120/20480 132/20480 (raw_FHSVB16e4) rising: +12->+15 dB p=0.24
    - R5-genie @16 1/20480 0/20480 0/20480 0/20480 (raw_FHSVB16e4) rising: +3->+6 dB p=0.89
    - R3-bigamp @16 6021/20480 5791/20480 6126/20480 6030/20480 (raw_FHU28B16e4) rising: +9->+12 dB p=0.00014
    - R3-bigamp @16 6258/20480 5952/20480 6266/20480 6284/20480 (raw_FHMXB16e4) rising: +9->+12 dB p=0.00036; +12->+15 dB p=0.43
- `paper_f22.txt` (10-08 06:17:18 KST, 96 줄): 
    - R5-genie @16 1/20480 0/20480 0/20480 0/20480 (raw_FHSVB16e4) rising: +3->+6 dB p=0.89
- `paper_f24.txt` (10-08 06:18:25 KST, 126 줄): 
    - R3-bigamp @16 1159/20480 1047/20480 1205/20480 1146/20480 (raw_FHROTaB16e4k) rising: +9->+12 dB p=0.00033
    - R3-bigamp @16 1362/20480 1299/20480 1418/20480 1397/20480 (raw_FHROTbB16e4k) rising: +9->+12 dB p=0.0096
- `paper_f31.txt` (10-08 06:16:22 KST, 49 줄): 없음
