## run log
[prior_eval DMCB16e4 10-10 20:04 CDT] start (git 27737b62) prior=DMC bstar=kron kron_K=4096 ll_val=122.37953759128766 best=65b26ddd4f6437f4 last=92dc9f53c31af875 ckpt=d2sx_DMC_N160000_a1
[prior_eval DMCB16e4 10-10 21:00 CDT] run DMCB16e4 (measurement) done
[prior_eval DMCB16e4 10-10 21:00 CDT] analysis DMCB16e4 rc=0
[prior_eval DMCB16e4 10-10 21:52 CDT] DMCB16e4last done
[prior_eval DMCB16e4 10-10 21:52 CDT] decision SNRs (anchor b*, tag DMCB16e4): +9 +12 +15
[prior_eval DMCB16e4 10-10 21:53 CDT] acceptance rc=0 (ACCEPT: OK -- DMCB16e4, DMCB16e4last)
[prior_eval DMCB16e4 10-10 21:53 CDT] recovery diff rc=0 (secondary at decision SNRs: +9 +12 +15 vs D2 -3,0,3)
[prior_eval DMCB16e4 10-10 21:53 CDT] PRIOR_EVAL_DONE
DMCB16e4 ['[run] M-ours-dscore: ABSENT -- no GATE-PASSING checkpoint (04_SPEC §5 gates GA-GD): no gate-passing checkpoint for D2; recorded PASS rows: none (searched conf/results/gate_D2.txt and LADDER.md)', "[run] M-ours-dscore is NOT in this run.  The reason is written to every raw file as 'meta|dscore_status', so analysis.py reports its slot as BLOCKED / FAILED-VERIFICATION instead of quietly printing a table without it (01_RULES §6).", "[run] Stage C arms (10_SPEC §3b/§3c): M-ours-dscore-C-{V0,V1,V4} + the mandatory GMM control M-ours-bstar-scalar, from /home/HTJ/t2/conf/ckpt/d2sx_DMC_N160000_a1_best.pt (8x4) -- ON for ['C2'], ABSENT for []", '[run] Stage C checkpoint: sha256[:16]=65b26ddd4f6437f4 epoch=812 best_epoch=812 role=best 8x4', "[run] Stage C gate record: NO GATE RECORD mentions d2sx_DMC_N160000_a1_best.pt -- UNVERIFIED here.  (GA-GD are measurable on D1 only, 10_SPEC §5: a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)", "[run] D2 7 points x n=2560 -> 448 tasks on 192 workers (prior DMC, cells ['C2'], chunk 40) -> /home/HTJ/t2/conf/raw_DMCB16e4", '[run] finished in 55.9 min -> python runner.py analysis --testbed D2 --tag DMCB16e4']
DMCB16e4 tables head: ['# date        : 2026-10-11 11:00:45 KST', '# git commit  : 27737b62']
DMCB16e4last ['[run] M-ours-dscore: ABSENT -- no GATE-PASSING checkpoint (04_SPEC §5 gates GA-GD): no gate-passing checkpoint for D2; recorded PASS rows: none (searched conf/results/gate_D2.txt and LADDER.md)', "[run] M-ours-dscore is NOT in this run.  The reason is written to every raw file as 'meta|dscore_status', so analysis.py reports its slot as BLOCKED / FAILED-VERIFICATION instead of quietly printing a table without it (01_RULES §6).", "[run] Stage C arms (10_SPEC §3b/§3c): M-ours-dscore-C-{V0,V1,V4} + the mandatory GMM control M-ours-bstar-scalar, from /home/HTJ/t2/conf/ckpt/d2sx_DMC_N160000_a1.pt (8x4) -- ON for ['C2'], ABSENT for []", '[run] Stage C checkpoint: sha256[:16]=92dc9f53c31af875 epoch=832 best_epoch=812 role=last 8x4 | evaluated = LAST epoch; the best-epoch weights are in the _best.pt sibling', "[run] Stage C gate record: NO GATE RECORD mentions d2sx_DMC_N160000_a1.pt -- UNVERIFIED here.  (GA-GD are measurable on D1 only, 10_SPEC §5: a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)", "[run] D2 7 points x n=2560 -> 448 tasks on 192 workers (prior DMC, cells ['C2'], chunk 40) -> /home/HTJ/t2/conf/raw_DMCB16e4last", '[run] finished in 51.5 min -> python runner.py analysis --testbed D2 --tag DMCB16e4last']
DMCB16e4last tables head: ['# date        : 2026-10-11 11:52:22 KST', '# git commit  : 27737b62']

## table B blocks
[DMCB16e4] M-ours-bstar -> M-ours-dscore-C-V1
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 127:46 p=5.8e-10  +12 dB 111:42 p=2.2e-08  +15 dB 119:36 p=1.4e-11   pooled 357:124 p=3.4e-27
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V1): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] M-ours-bstar -> M-ours-bstar-scalar
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 45:42 p=0.83  +12 dB 36:35 p=1  +15 dB 35:38 p=0.82   pooled 116:115 p=1
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 0/3 points -> not significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-bstar-scalar): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] R2-ours-G -> M-ours-bstar
    decision SNRs ['+9', '+12', '+15'] (anchor R2-ours-G: |log10(BLER@16 of R2-ours-G / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 266:49 p=3.1e-37  +12 dB 236:48 p=5.5e-31  +15 dB 254:48 p=5.2e-35   pooled 756:145 p=2.3e-100
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus M-ours-bstar): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] M-ours-bstar -> M-ours-dscore-C-V4
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 131:44 p=3.1e-11  +12 dB 110:51 p=3.8e-06  +15 dB 124:33 p=1.3e-13   pooled 365:128 p=2e-27
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V4): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] M-ours-bstar -> M-ours-dscore-C-V4b
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 132:50 p=1e-09  +12 dB 112:52 p=3.2e-06  +15 dB 123:40 p=5.1e-11   pooled 367:142 p=5.6e-24
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V4b): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] M-ours-bstar -> M-ours-dscore-C-V0
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 17:885 p=2.5e-236  +12 dB 15:985 p=1.3e-268  +15 dB 28:929 p=1.1e-234   pooled 60:2799 p=0
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V0): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] M-ours-dscore-C-V1 -> R5-genie
    decision SNRs ['+9', '+12', '+15'] (anchor R5-genie: |log10(BLER@16 of R5-genie / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 237:22 p=1e-46  +12 dB 215:17 p=7.9e-45  +15 dB 208:18 p=3.7e-42   pooled 660:57 p=4.6e-131
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-dscore-C-V1 minus R5-genie): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4] M-ours-bstar -> R5-genie
    decision SNRs ['+9', '+12', '+15'] (anchor R5-genie: |log10(BLER@16 of R5-genie / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 319:23 p=8.4e-68  +12 dB 289:22 p=1.5e-60  +15 dB 282:9 p=1.9e-71   pooled 890:54 p=5.9e-196
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus R5-genie): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-bstar -> M-ours-dscore-C-V1
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 126:44 p=2.3e-10  +12 dB 110:46 p=3.2e-07  +15 dB 124:36 p=1.6e-12   pooled 360:126 p=3.9e-27
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V1): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-bstar -> M-ours-bstar-scalar
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 45:42 p=0.83  +12 dB 36:35 p=1  +15 dB 35:38 p=0.82   pooled 116:115 p=1
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 0/3 points -> not significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-bstar-scalar): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] R2-ours-G -> M-ours-bstar
    decision SNRs ['+9', '+12', '+15'] (anchor R2-ours-G: |log10(BLER@16 of R2-ours-G / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 266:49 p=3.1e-37  +12 dB 236:48 p=5.5e-31  +15 dB 254:48 p=5.2e-35   pooled 756:145 p=2.3e-100
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (R2-ours-G minus M-ours-bstar): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-bstar -> M-ours-dscore-C-V4
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 131:45 p=6.1e-11  +12 dB 112:54 p=7.9e-06  +15 dB 126:43 p=1.2e-10   pooled 369:142 p=2.7e-24
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V4): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-bstar -> M-ours-dscore-C-V4b
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 131:45 p=6.1e-11  +12 dB 112:54 p=7.9e-06  +15 dB 126:42 p=6e-11   pooled 369:141 p=1.5e-24
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V4b): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-bstar -> M-ours-dscore-C-V0
    decision SNRs ['+9', '+12', '+15'] (anchor M-ours-bstar: |log10(BLER@16 of M-ours-bstar / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 17:883 p=9.7e-236  +12 dB 15:999 p=9.8e-273  +15 dB 17:1038 p=3.2e-281   pooled 49:2920 p=0
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 0/3 points, first arm fewer failures at 3/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus M-ours-dscore-C-V0): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-dscore-C-V1 -> R5-genie
    decision SNRs ['+9', '+12', '+15'] (anchor R5-genie: |log10(BLER@16 of R5-genie / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 238:24 p=1.8e-45  +12 dB 222:19 p=4.4e-45  +15 dB 205:20 p=7.8e-40   pooled 665:63 p=1e-127
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-dscore-C-V1 minus R5-genie): n/a (>  15 vs >  15) — extend the SNR grid
[DMCB16e4last] M-ours-bstar -> R5-genie
    decision SNRs ['+9', '+12', '+15'] (anchor R5-genie: |log10(BLER@16 of R5-genie / 0.1)| smallest, BLER in [0.005, 0.9])
    sign test @16: +9 dB 319:23 p=8.4e-68  +12 dB 289:22 p=1.5e-60  +15 dB 282:9 p=1.9e-71   pooled 890:54 p=5.9e-196
    power guard: 3 decision points, 3 with >= 6 discordant pairs -> POWERED
    two-sided sign test at p < .05: second arm fewer failures at 3/3 points, first arm fewer failures at 0/3 points -> significant
    SNR@0.1 gap (M-ours-bstar minus R5-genie): n/a (>  15 vs >  15) — extend the SNR grid

## BLER@16 (R0-pilot also @1) and failure counts, tag DMCB16e4  SNR [-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0]
M-ours-bstar           BLER 0.872 / 0.713 / 0.620 / 0.536 / 0.478 / 0.399 / 0.345   fails 2232 / 1826 / 1586 / 1372 / 1223 / 1021 / 884   n 2560
M-ours-bstar-scalar    BLER 0.879 / 0.718 / 0.624 / 0.540 / 0.477 / 0.398 / 0.346   fails 2249 / 1837 / 1597 / 1383 / 1220 / 1020 / 887   n 2560
M-ours-dscore-C-V0     BLER 0.970 / 0.928 / 0.889 / 0.859 / 0.817 / 0.778 / 0.697   fails 2484 / 2375 / 2277 / 2200 / 2091 / 1991 / 1785   n 2560
M-ours-dscore-C-V1     BLER 0.834 / 0.680 / 0.588 / 0.500 / 0.446 / 0.372 / 0.313   fails 2136 / 1742 / 1505 / 1281 / 1142 / 952 / 801   n 2560
M-ours-dscore-C-V4     BLER 0.839 / 0.683 / 0.592 / 0.503 / 0.444 / 0.376 / 0.310   fails 2148 / 1749 / 1515 / 1287 / 1136 / 962 / 793   n 2560
M-ours-dscore-C-V4b    BLER 0.837 / 0.692 / 0.590 / 0.505 / 0.446 / 0.375 / 0.313   fails 2142 / 1771 / 1510 / 1293 / 1141 / 961 / 801   n 2560
M-ours-gmm32           BLER 0.887 / 0.762 / 0.661 / 0.571 / 0.518 / 0.432 / 0.380   fails 2270 / 1951 / 1693 / 1463 / 1325 / 1106 / 973   n 2560
R0-pilot               BLER 0.943 / 0.827 / 0.718 / 0.632 / 0.567 / 0.491 / 0.437   fails 2413 / 2117 / 1838 / 1618 / 1451 / 1256 / 1119   n 2560
R0-pilot@1             BLER 0.987 / 0.943 / 0.870 / 0.811 / 0.747 / 0.666 / 0.621   fails 2527 / 2413 / 2227 / 2077 / 1913 / 1705 / 1590   n 2560
R1-turbo               BLER 0.957 / 0.877 / 0.772 / 0.679 / 0.598 / 0.505 / 0.452   fails 2451 / 2246 / 1976 / 1739 / 1532 / 1293 / 1158   n 2560
R2-ours-G              BLER 0.910 / 0.801 / 0.704 / 0.622 / 0.562 / 0.472 / 0.426   fails 2330 / 2050 / 1801 / 1592 / 1440 / 1209 / 1090   n 2560
R3-bigamp              BLER 0.961 / 0.869 / 0.792 / 0.747 / 0.754 / 0.746 / 0.764   fails 2461 / 2224 / 2028 / 1913 / 1929 / 1910 / 1957   n 2560
R4-llr                 BLER 0.986 / 0.959 / 0.921 / 0.885 / 0.853 / 0.791 / 0.760   fails 2523 / 2455 / 2358 / 2266 / 2184 / 2025 / 1945   n 2560
R4-scvamp              BLER 0.968 / 0.907 / 0.830 / 0.773 / 0.711 / 0.647 / 0.607   fails 2477 / 2322 / 2125 / 1978 / 1820 / 1656 / 1554   n 2560
R5-genie               BLER 0.686 / 0.569 / 0.484 / 0.409 / 0.362 / 0.295 / 0.239   fails 1756 / 1457 / 1238 / 1048 / 927 / 754 / 611   n 2560
R0-pilot (@1)          BLER 0.987 / 0.943 / 0.870 / 0.811 / 0.747 / 0.666 / 0.621   fails 2527 / 2413 / 2227 / 2077 / 1913 / 1705 / 1590
V1 (last tag)          BLER 0.834 / 0.682 / 0.593 / 0.502 / 0.446 / 0.374 / 0.311   fails 2136 / 1745 / 1518 / 1286 / 1141 / 957 / 796

## best vs last V1, paired exact two-sided sign test at the decision SNRs [9.0, 12.0, 15.0] (a = only best fails, b = only last fails)
  +9 dB 18:17 p=1
  +12 dB 10:15 p=0.424
  +15 dB 17:12 p=0.458
  pooled 45:44 p=1

----- results/review_next/DMCB16e4_accept.txt
ACCEPT: OK -- DMCB16e4, DMCB16e4last

----- results/review_next/recovery_DMCB16e4.txt
# recovery R = (b* - V1)/(b* - genie) @16, raw_DMCB16e4 C2, paired bootstrap B=2000 seed=20260926, 90% CI
  -3 dB  b* 2232  V1 2136  genie 1756  n=2560  R = 0.202  [90% 0.166, 0.240]
  pooled 1 SNRs  b* 2232  V1 2136  genie 1756  R = 0.202  [90% 0.166, 0.240]
# recovery R = (b* - V1)/(b* - genie) @16, raw_DMCB16e4 C2, paired bootstrap B=2000 seed=20260926, 90% CI
  +9 dB  b* 1223  V1 1142  genie 927  n=2560  R = 0.274  [90% 0.208, 0.336]
  +12 dB  b* 1021  V1 952  genie 754  n=2560  R = 0.258  [90% 0.191, 0.323]
  +15 dB  b* 884  V1 801  genie 611  n=2560  R = 0.304  [90% 0.238, 0.369]
  pooled 3 SNRs  b* 3128  V1 2895  genie 2292  R = 0.279  [90% 0.241, 0.316]

----- results/review_next/recovery_DMCB16e4last.txt
# recovery R = (b* - V1)/(b* - genie) @16, raw_DMCB16e4last C2, paired bootstrap B=2000 seed=20260926, 90% CI
  -3 dB  b* 2232  V1 2136  genie 1756  n=2560  R = 0.202  [90% 0.165, 0.242]
  pooled 1 SNRs  b* 2232  V1 2136  genie 1756  R = 0.202  [90% 0.165, 0.242]
# recovery R = (b* - V1)/(b* - genie) @16, raw_DMCB16e4last C2, paired bootstrap B=2000 seed=20260926, 90% CI
  +9 dB  b* 1223  V1 1141  genie 927  n=2560  R = 0.277  [90% 0.214, 0.338]
  +12 dB  b* 1021  V1 957  genie 754  n=2560  R = 0.240  [90% 0.171, 0.306]
  +15 dB  b* 884  V1 796  genie 611  n=2560  R = 0.322  [90% 0.254, 0.388]
  pooled 3 SNRs  b* 3128  V1 2894  genie 2292  R = 0.280  [90% 0.242, 0.318]

----- results/review_next/recovery_diff_DMCB16e4.txt
# recovery R = (b* - V1)/(b* - genie) @16; paired bootstrap per raw set (three arms together), the two raw sets resampled independently (UNPAIRED difference); B=2000, seed=20260926, 90% CI
  R1: raw_DMCB16e4 C2 SNR ['-3']  b* 2232 V1 2136 genie 1756  R = 0.202  [90% 0.165, 0.240]
  R2: raw_B16e4k C2 SNR ['-3']  b* 623 V1 371 genie 87  R = 0.470  [90% 0.427, 0.512]
  R1 - R2 = -0.268  [90% unpaired -0.325, -0.209]  undefined replicates 0
  R1 - R2 = -0.268  [90% unpaired -0.325, -0.209]  bootstrap two-sided p = 0.0000  (--level 0.9)
  gaps R1: SigmaF_V1 - SigmaF_g = 380  [90% 351, 410]   SigmaF_b* - SigmaF_g = 476  [90% 445, 509]   (blocks, summed over SNR ['-3'])
  gaps R2: SigmaF_V1 - SigmaF_g = 284  [90% 256, 311]   SigmaF_b* - SigmaF_g = 536  [90% 501, 571]   (blocks, summed over SNR ['-3'])
# recovery R = (b* - V1)/(b* - genie) @16; paired bootstrap per raw set (three arms together), the two raw sets resampled independently (UNPAIRED difference); B=2000, seed=20260926, 90% CI
  R1: raw_DMCB16e4last C2 SNR ['-3']  b* 2232 V1 2136 genie 1756  R = 0.202  [90% 0.164, 0.242]
  R2: raw_B16e4k C2 SNR ['-3']  b* 623 V1 371 genie 87  R = 0.470  [90% 0.427, 0.512]
  R1 - R2 = -0.268  [90% unpaired -0.326, -0.208]  undefined replicates 0
  R1 - R2 = -0.268  [90% unpaired -0.326, -0.208]  bootstrap two-sided p = 0.0000  (--level 0.9)
  gaps R1: SigmaF_V1 - SigmaF_g = 380  [90% 350, 410]   SigmaF_b* - SigmaF_g = 476  [90% 445, 509]   (blocks, summed over SNR ['-3'])
  gaps R2: SigmaF_V1 - SigmaF_g = 284  [90% 256, 311]   SigmaF_b* - SigmaF_g = 536  [90% 501, 571]   (blocks, summed over SNR ['-3'])
# recovery R = (b* - V1)/(b* - genie) @16; paired bootstrap per raw set (three arms together), the two raw sets resampled independently (UNPAIRED difference); B=2000, seed=20260926, 90% CI
  R1: raw_DMCB16e4 C2 SNR ['+9', '+12', '+15']  b* 3128 V1 2895 genie 2292  R = 0.279  [90% 0.242, 0.316]
  R2: raw_B16e4k C2 SNR ['-3', '+0', '+3']  b* 864 V1 488 genie 125  R = 0.509  [90% 0.470, 0.544]
  R1 - R2 = -0.230  [90% unpaired -0.280, -0.178]  undefined replicates 0
  R1 - R2 = -0.230  [90% unpaired -0.280, -0.178]  bootstrap two-sided p = 0.0000  (--level 0.9)
  gaps R1: SigmaF_V1 - SigmaF_g = 603  [90% 560, 644]   SigmaF_b* - SigmaF_g = 836  [90% 787, 883]   (blocks, summed over SNR ['+9', '+12', '+15'])
  gaps R2: SigmaF_V1 - SigmaF_g = 363  [90% 332, 396]   SigmaF_b* - SigmaF_g = 739  [90% 697, 781]   (blocks, summed over SNR ['-3', '+0', '+3'])

----- results/guard_D2_DMCB16e4.txt
# date        : 2026-10-11 11:52:30 KST
# git commit  : 27737b62
# versions    : python 3.12.14  numpy 2.5.2  scipy 1.18.1  torch 2.14.0+cu130 (cuda_available=False)
# device      : CPU (192 cores) | dtype: complex128 / float64 | deterministic: yes (fixed seeds, no GPU in the receiver)
# testbed     : D2
# seed rule   : default_rng([20260926, TBID[testbed], PID[prior], Nr, T, Tp, int(snr)+100])  (trials of a point = ONE stream)
# code        : rate-1/2 conv (133,171)_8 nu=6 terminated, QPSK, outer iterations = 16 for EVERY arm
# Demo/ hashes: t2_route_a.py=95a5408901ec125c  t2_trellis.py=31cd0ee9c68e972b  t2_gmm.py=d064e58c7510c769
# content     : (F3) Module H divergence guard firings, DIVERGE_NMSE = 10.0 (reused from code/bigamp.py, NOT re-chosen)
# raw         : raw_DMCB16e4
# rule        : a trial fires the guard if NMSE > 10.0 or non-finite at ANY of the 16 iterations.
# status      : DETECTION AND CLASSIFICATION ONLY -- no arm's trajectory is altered, so every
#               number recorded before this guard existed remains valid.
# read-only   : the raw files are not rewritten.

cell    SNR arm                        fired     of    rate  worst NMSE seen
------------------------------------------------------------------------------
C2       -3 M-ours-dscore-C-V0          2295   2560   0.896  1.485e+12
C2       -3 M-ours-dscore-C-V1             1   2560   0.000  11.17
C2       -3 M-ours-dscore-C-V4             1   2560   0.000  11.31
C2       -3 M-ours-dscore-C-V4b            1   2560   0.000  10.1
C2       -3 M-ours-gmm32                   1   2560   0.000  11.49
C2       -3 R1-turbo                       1   2560   0.000  18.51
C2       -3 R2-ours-G                      1   2560   0.000  18.45
C2       -3 R4-llr                         1   2560   0.000  17.65
C2       -3 R4-scvamp                      1   2560   0.000  17.65
C2       +0 M-ours-dscore-C-V0          2181   2560   0.852  1.436e+09
C2       +0 R1-turbo                       1   2560   0.000  10.65
C2       +0 R2-ours-G                      1   2560   0.000  10.8
C2       +0 R4-llr                         1   2560   0.000  10.3
C2       +0 R4-scvamp                      1   2560   0.000  10.3
C2       +3 M-ours-dscore-C-V0          1824   2560   0.713  8.242e+07
C2       +6 M-ours-dscore-C-V0          1734   2560   0.677  7.612e+06
C2       +9 M-ours-dscore-C-V0          1480   2560   0.578  1.574e+09
C2      +12 M-ours-dscore-C-V0          1403   2560   0.548  4.275e+10
C2      +15 M-ours-dscore-C-V0          1070   2560   0.418  8.219e+07

arms that NEVER fired the guard anywhere in this raw set (4): M-ours-bstar, M-ours-bstar-scalar, R0-pilot, R3-bigamp
not applicable -- no channel estimate, so no Module H path (1): R5-genie

----- results/guard_D2_DMCB16e4last.txt
# date        : 2026-10-11 11:52:45 KST
# git commit  : 27737b62
# versions    : python 3.12.14  numpy 2.5.2  scipy 1.18.1  torch 2.14.0+cu130 (cuda_available=False)
# device      : CPU (192 cores) | dtype: complex128 / float64 | deterministic: yes (fixed seeds, no GPU in the receiver)
# testbed     : D2
# seed rule   : default_rng([20260926, TBID[testbed], PID[prior], Nr, T, Tp, int(snr)+100])  (trials of a point = ONE stream)
# code        : rate-1/2 conv (133,171)_8 nu=6 terminated, QPSK, outer iterations = 16 for EVERY arm
# Demo/ hashes: t2_route_a.py=95a5408901ec125c  t2_trellis.py=31cd0ee9c68e972b  t2_gmm.py=d064e58c7510c769
# content     : (F3) Module H divergence guard firings, DIVERGE_NMSE = 10.0 (reused from code/bigamp.py, NOT re-chosen)
# raw         : raw_DMCB16e4last
# rule        : a trial fires the guard if NMSE > 10.0 or non-finite at ANY of the 16 iterations.
# status      : DETECTION AND CLASSIFICATION ONLY -- no arm's trajectory is altered, so every
#               number recorded before this guard existed remains valid.
# read-only   : the raw files are not rewritten.

cell    SNR arm                        fired     of    rate  worst NMSE seen
------------------------------------------------------------------------------
C2       -3 M-ours-dscore-C-V0          2290   2560   0.895  3.86e+09
C2       -3 M-ours-dscore-C-V1             1   2560   0.000  11.44
C2       -3 M-ours-dscore-C-V4             1   2560   0.000  11.93
C2       -3 M-ours-dscore-C-V4b            1   2560   0.000  10.51
C2       -3 M-ours-gmm32                   1   2560   0.000  11.49
C2       -3 R1-turbo                       1   2560   0.000  18.51
C2       -3 R2-ours-G                      1   2560   0.000  18.45
C2       -3 R4-llr                         1   2560   0.000  17.65
C2       -3 R4-scvamp                      1   2560   0.000  17.65
C2       +0 M-ours-dscore-C-V0          2153   2560   0.841  1.608e+09
C2       +0 R1-turbo                       1   2560   0.000  10.65
C2       +0 R2-ours-G                      1   2560   0.000  10.8
C2       +0 R4-llr                         1   2560   0.000  10.3
C2       +0 R4-scvamp                      1   2560   0.000  10.3
C2       +3 M-ours-dscore-C-V0          1823   2560   0.712  2.676e+09
C2       +6 M-ours-dscore-C-V0          1683   2560   0.657  1.904e+07
C2       +9 M-ours-dscore-C-V0          1478   2560   0.577  7.29e+09
C2      +12 M-ours-dscore-C-V0          1418   2560   0.554  7.794e+08
C2      +15 M-ours-dscore-C-V0          1114   2560   0.435  7.912e+10

arms that NEVER fired the guard anywhere in this raw set (4): M-ours-bstar, M-ours-bstar-scalar, R0-pilot, R3-bigamp
not applicable -- no channel estimate, so no Module H path (1): R5-genie

----- results/review_next/DMCB16e4_leak_strata.txt
# date        : 2026-10-11 11:56:46 KST
# git commit  : 3ddb0831
# versions    : python 3.12.14  numpy 2.5.2  scipy 1.18.1  torch 2.14.0+cu130 (cuda_available=False)
# device      : CPU (192 cores) | dtype: complex128 / float64 | deterministic: yes (fixed seeds, no GPU in the receiver)
# testbed     : D2
# seed rule   : default_rng([20260926, TBID[testbed], PID[prior], Nr, T, Tp, int(snr)+100])  (trials of a point = ONE stream)
# code        : rate-1/2 conv (133,171)_8 nu=6 terminated, QPSK, outer iterations = 16 for EVERY arm
# Demo/ hashes: t2_route_a.py=95a5408901ec125c  t2_trellis.py=31cd0ee9c68e972b  t2_gmm.py=d064e58c7510c769
# content     : dmc_leak_strata.py -- leakage strata of raw_DMCB16e4 (prior DMC, cell C2), REPORT-ONLY (NEXT_EXPERIMENTS_DMC16e4 §1): d = min_train ||h - h_train||^2 / ||h||^2, N' = 160000 (stream 7), strata d < 0.1 / d >= 0.1; decision SNRs [9.0, 12.0, 15.0] from tables_D2_DMCB16e4.txt

+9 dB  n=2560  alignment (R5-genie, first 40 replayed trials vs raw, bit-identical): OK;  d median 0.1242, share d < 0.1 = 0.438
    d < 0.1    n= 1121  failures b*  904  V1  860  genie  716  R = 0.234
    d >= 0.1   n= 1439  failures b*  319  V1  282  genie  211  R = 0.343
+12 dB  n=2560  alignment (R5-genie, first 40 replayed trials vs raw, bit-identical): OK;  d median 0.1431, share d < 0.1 = 0.396
    d < 0.1    n= 1013  failures b*  759  V1  723  genie  594  R = 0.218
    d >= 0.1   n= 1547  failures b*  262  V1  229  genie  160  R = 0.324
+15 dB  n=2560  alignment (R5-genie, first 40 replayed trials vs raw, bit-identical): OK;  d median 0.1258, share d < 0.1 = 0.433
    d < 0.1    n= 1109  failures b*  713  V1  654  genie  525  R = 0.314
    d >= 0.1   n= 1451  failures b*  171  V1  147  genie   86  R = 0.282
pooled over the 3 decision SNRs
    d < 0.1    n= 3243  failures b* 2376  V1 2237  genie 1835  R = 0.257
    d >= 0.1   n= 4437  failures b*  752  V1  658  genie  457  R = 0.319

alignment OK at every SNR
report-only: no label, no test, no CI; interpretation is the user's.
results/review_next/run_manifest_DMCB16e4.json exists ['"git_commit": "27737b62"', '"config_hash": "e840f96a01f9bca2"', '"git": "27737b62"']
results/review_next/run_manifest_DMCB16e4last.json exists ['"git_commit": "27737b62"', '"config_hash": "e840f96a01f9bca2"', '"git": "27737b62"']
