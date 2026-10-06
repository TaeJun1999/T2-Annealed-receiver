### 6.1 결과 (기록 2026-10-06 15:07 CDT (= 10-07 05:07 KST), Opus 5.5 (주 세션, 생성기 s6_gen.py) — 전사만, 해석 없음; 초안 = 스크래치 생성기 `s6_gen.py` 의 출력 (자리표시 **[판단 필요: …]**·**[입력 없음: …]** 은 기록자가 채운다); 원본 `logs/run_nscale.log`·`logs/run_D2_<T>.log` (청크별 BLER 줄은 옮기지 않음)·`logs/analysis_<T>.log`, `results/tables_D2_<T>.txt`·`results/guard_D2_<T>.txt`, `results/review_next/nscale_{P1_<T>,P2_C2,P2_C6,P2_holm,qk_<c>_L<L>{,_qkN,_qkB},S1_C2,S2_C2,eff_C2,eff128_C2,K8,K8_V1}.txt`·`<K>_accept.txt`·`recovery_<T>{,last}.txt`·`run_manifest_<T>.json`, `results/nscale/nscale_s5.txt`·`nscale_prep.txt`·`logs/nscale/nscale_s5.start`, raw `raw_<T>/` (meta·run 키, best/last V1 blk_err))

표기: `L:n` = `logs/run_nscale.log` n 행. 접두 없는 이름은 `results/review_next/nscale_<이름>.txt` (예: `P2_C2:4`), `acc_<K>` = `results/review_next/<K>_accept.txt`, `rec_<T>` = `results/review_next/recovery_<T>.txt`, `man_<T>` = `results/review_next/run_manifest_<T>.json`, `tab_<T>` = `results/tables_D2_<T>.txt`, `guard_<T>` = `results/guard_D2_<T>.txt`, `run_<T>` = `logs/run_D2_<T>.log`, `an_<T>` = `logs/analysis_<T>.log`, `S5` = `results/nscale/nscale_s5.txt`, `prep` = `results/nscale/nscale_prep.txt` (§5 커밋본), `reg` = 이 문서; `:n` = 그 파일 n 행. 시각은 로그 원값 CDT (KST 는 `date` 로 환산). "기록자 산술" = 파일의 정수 실패 수·값에서 Python 으로 계산 (`s6_gen.py`; 정확한 R 은 실패 수의 분수, 표시 값은 파일의 세 자리).

**동결·실행 커밋**: 동결 `2d50dab51629c1731ec41db2f7ed1449ae7ea9d1` (`S5:3`). 실행 커밋 = §5 커밋 **68d4d353** (68d4d353a24eeb2233007c8225787e03764cade1, 커밋 시각 2026-10-06 08:11:08 CDT; `git log -1 -- results/nscale/nscale_s5.txt`) — 동결이 조상: 예; `git diff 2d50dab5 68d4d353 -- code ../Demo` 0 바이트 (수용 (f)·실행 위치 행); 동결 대비 바뀐 파일 `git diff --name-status`: M conf/DECISIONS.md; M conf/conference_plot/F16_headline_budget.pdf; M conf/conference_plot/F16_headline_budget.png; M conf/conference_plot/F17_codim_C6.pdf; M conf/conference_plot/F17_codim_C6.png; M conf/conference_plot/F18_oog_rule_K2.pdf; M conf/conference_plot/F18_oog_rule_K2.png; M conf/conference_plot/F19_pilot_pareto.pdf; M conf/conference_plot/F19_pilot_pareto.png; M conf/conference_plot/F20_channel_models.pdf; M conf/conference_plot/F20_channel_models.png; M conf/conference_plot/F21_all_baselines.pdf; M conf/conference_plot/F21_all_baselines.png; M conf/conference_plot/F22_pilot_only.pdf; M conf/conference_plot/F22_pilot_only.png; M conf/conference_plot/F23_mismatch.pdf; M conf/conference_plot/F23_mismatch.png; M conf/conference_plot/F24_nonstationary_D2C2.pdf; M conf/conference_plot/F24_nonstationary_D2C2.png; M conf/conference_plot/F25_nonstationary_all.pdf; M conf/conference_plot/F25_nonstationary_all.png; M conf/conference_plot/F26_drift_spatial.pdf; M conf/conference_plot/F26_drift_spatial.png; M conf/conference_plot/F27_nonstationary_gap_recovery.pdf; M conf/conference_plot/F27_nonstationary_gap_recovery.png; M conf/conference_plot/F28_nonstationary_C6.pdf; M conf/conference_plot/F28_nonstationary_C6.png; M conf/conference_plot/F29_label_grid.pdf; M conf/conference_plot/F29_label_grid.png; M conf/conference_plot/F30_scale_trend.pdf; M conf/conference_plot/F30_scale_trend.png; M conf/conference_plot/F31_sparse_baselines.pdf; M conf/conference_plot/F31_sparse_baselines.png; M conf/conference_plot/F32_hisnr_highsnr.pdf; M conf/conference_plot/F32_hisnr_highsnr.png; M conf/conference_plot/README.md; M conf/figs/F16_headline_budget.pdf; M conf/figs/F16_headline_budget.png; M conf/figs/F17_codim_C6.pdf; M conf/figs/F17_codim_C6.png; M conf/figs/F18_oog_rule_K2.pdf; M conf/figs/F18_oog_rule_K2.png; M conf/figs/F19_pilot_pareto.pdf; M conf/figs/F19_pilot_pareto.png; M conf/figs/F20_channel_models.pdf; M conf/figs/F20_channel_models.png; M conf/figs/F21_all_baselines.pdf; M conf/figs/F21_all_baselines.png; M conf/figs/F22_pilot_only.pdf; M conf/figs/F22_pilot_only.png; M conf/figs/F23_mismatch.pdf; M conf/figs/F23_mismatch.png; M conf/figs/F24_nonstationary_D2C2.pdf; M conf/figs/F24_nonstationary_D2C2.png; M conf/figs/F25_nonstationary_all.pdf; M conf/figs/F25_nonstationary_all.png; M conf/figs/F26_drift_spatial.pdf; M conf/figs/F26_drift_spatial.png; M conf/figs/F27_nonstationary_gap_recovery.pdf; M conf/figs/F27_nonstationary_gap_recovery.png; M conf/figs/F28_nonstationary_C6.pdf; M conf/figs/F28_nonstationary_C6.png; M conf/figs/F29_label_grid.pdf; M conf/figs/F29_label_grid.png; M conf/figs/F30_scale_trend.pdf; M conf/figs/F30_scale_trend.png; M conf/figs/F31_sparse_baselines.pdf; M conf/figs/F31_sparse_baselines.png; M conf/figs/F32_hisnr_highsnr.pdf; M conf/figs/F32_hisnr_highsnr.png; M conf/results/d2_gbprime.csv; A conf/results/guard_D2_NR32B16e4s2.txt; A conf/results/guard_D2_NR32B16e4s3.txt; A conf/results/guard_D2_U28NR16B16e4s2.txt; A conf/results/guard_D2_U28NR16B16e4s3.txt; A conf/results/guard_D2_U28NR32B16e4s2.txt; A conf/results/guard_D2_U28NR32B16e4s3.txt; A conf/results/nscale/nscale_links.txt; A conf/results/nscale/nscale_prep.txt; A conf/results/nscale/nscale_s5.txt; M conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md; A conf/results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md; A conf/results/review_next/NR32B16e4s2_accept.txt; A conf/results/review_next/NR32B16e4s2_refarms.txt; A conf/results/review_next/NR32B16e4s3_accept.txt; A conf/results/review_next/NR32B16e4s3_refarms.txt; A conf/results/review_next/U28NR16B16e4chkS2_accept.txt; A conf/results/review_next/U28NR16B16e4chkS_accept.txt; A conf/results/review_next/U28NR16B16e4s2_accept.txt; A conf/results/review_next/U28NR16B16e4s2_refarms.txt; A conf/results/review_next/U28NR16B16e4s3_accept.txt; A conf/results/review_next/U28NR16B16e4s3_refarms.txt; A conf/results/review_next/U28NR32B16e4s2_accept.txt; A conf/results/review_next/U28NR32B16e4s2_refarms.txt; A conf/results/review_next/U28NR32B16e4s3_accept.txt; A conf/results/review_next/U28NR32B16e4s3_refarms.txt; M conf/results/review_next/WORK_QUEUE.md; A conf/results/review_next/prereg_audit_2026-10-04/appended_61.txt; A conf/results/review_next/prereg_audit_2026-10-04/appended_dec315.txt; A conf/results/review_next/prereg_audit_2026-10-04/appended_exp59.txt; A conf/results/review_next/prereg_audit_2026-10-04/audit_SEEDSNR16e4.md; A conf/results/review_next/prereg_audit_2026-10-04/seedsnr_extra.out; A conf/results/review_next/prereg_audit_2026-10-04/seedsnr_extra.py; A conf/results/review_next/prereg_audit_2026-10-04/seedsnr_recompute.err; A conf/results/review_next/prereg_audit_2026-10-04/seedsnr_recompute.out; A conf/results/review_next/prereg_audit_2026-10-04/seedsnr_recompute.py; A conf/results/review_next/prereg_reviews_seedsnr/review_SEEDSNR16e4.md; A conf/results/review_next/recovery_NR32B16e4s2.txt; A conf/results/review_next/recovery_NR32B16e4s3.txt; A conf/results/review_next/recovery_U28NR16B16e4s2.txt; A conf/results/review_next/recovery_U28NR16B16e4s3.txt; A conf/results/review_next/recovery_U28NR32B16e4s2.txt; A conf/results/review_next/recovery_U28NR32B16e4s3.txt; A conf/results/review_next/run_manifest_NR32B16e4s2.json; A conf/results/review_next/run_manifest_NR32B16e4s3.json; A conf/results/review_next/run_manifest_U28NR16B16e4s2.json; A conf/results/review_next/run_manifest_U28NR16B16e4s3.json; A conf/results/review_next/run_manifest_U28NR32B16e4s2.json; A conf/results/review_next/run_manifest_U28NR32B16e4s3.json; A conf/results/review_next/seedsnr_dR_NR32B16e4s2.txt; A conf/results/review_next/seedsnr_dR_NR32B16e4s3.txt; A conf/results/review_next/seedsnr_dR_U28NR16B16e4s2.txt; A conf/results/review_next/seedsnr_dR_U28NR16B16e4s3.txt; A conf/results/review_next/seedsnr_dR_U28NR32B16e4s2.txt; A conf/results/review_next/seedsnr_dR_U28NR32B16e4s3.txt; M conf/results/samplecx.csv; A conf/results/scale/seedsnr_s5.txt; A conf/results/tables_D2_NR32B16e4s2.txt; A conf/results/tables_D2_NR32B16e4s3.txt; A conf/results/tables_D2_U28NR16B16e4s2.txt; A conf/results/tables_D2_U28NR16B16e4s3.txt; A conf/results/tables_D2_U28NR32B16e4s2.txt; A conf/results/tables_D2_U28NR32B16e4s3.txt; A conference/PAPER_PLAN.md; M conference/README.md; M conference/RESULTS_snapshot.md; A conference/figures/F16_headline_budget.pdf; A conference/figures/F16_headline_budget.png; A conference/figures/F17_codim_C6.pdf; A conference/figures/F17_codim_C6.png; A conference/figures/F18_oog_rule_K2.pdf; A conference/figures/F18_oog_rule_K2.png; A conference/figures/F19_pilot_pareto.pdf; A conference/figures/F19_pilot_pareto.png; A conference/figures/F20_channel_models.pdf; A conference/figures/F20_channel_models.png; A conference/figures/F21_all_baselines.pdf; A conference/figures/F21_all_baselines.png; A conference/figures/F22_pilot_only.pdf; A conference/figures/F22_pilot_only.png; A conference/figures/F23_mismatch.pdf; A conference/figures/F23_mismatch.png; A conference/figures/F24_nonstationary_D2C2.pdf; A conference/figures/F24_nonstationary_D2C2.png; A conference/figures/F25_nonstationary_all.pdf; A conference/figures/F25_nonstationary_all.png; A conference/figures/F26_drift_spatial.pdf; A conference/figures/F26_drift_spatial.png; A conference/figures/F27_nonstationary_gap_recovery.pdf; A conference/figures/F27_nonstationary_gap_recovery.png; A conference/figures/F28_nonstationary_C6.pdf; A conference/figures/F28_nonstationary_C6.png; A conference/figures/F29_label_grid.pdf; A conference/figures/F29_label_grid.png; A conference/figures/F30_scale_trend.pdf; A conference/figures/F30_scale_trend.png; A conference/figures/F30top_col.pdf; A conference/figures/F30top_col.png; A conference/figures/F30top_wide.pdf; A conference/figures/F30top_wide.png; A conference/figures/F31_sparse_baselines.pdf; A conference/figures/F31_sparse_baselines.png; A conference/figures/F32_hisnr_highsnr.pdf; A conference/figures/F32_hisnr_highsnr.png; A conference/figures/README.md; A conference/figures/TERMS.md; A conference/figures/paper_f16.py; A conference/figures/paper_f17.py; A conference/figures/paper_f18.py; A conference/figures/paper_f19.py; A conference/figures/paper_f20.py; A conference/figures/paper_f21.py; A conference/figures/paper_f22.py; A conference/figures/paper_f23.py; A conference/figures/paper_f24.py; A conference/figures/paper_f27.py; A conference/figures/paper_f30.py; A conference/figures/paper_f30top.py; A conference/figures/paper_f31.py; A conference/figures/paper_f32.py; A conference/tables/README.md; A conference/tables/table1.tex; A conference/tables/table1_compact.tex; A conference/tables/table1_sources.md; A conference/tools/regen_notitle.py; A conference/tools/sync_paper_branch.sh; M docs/EXPERIMENTS.md; M docs/RESULTS.md; M docs/paper/CONTRIBUTIONS.md. 이 기록 시점 HEAD = 68d4d353 (실행 커밋 뒤 커밋 0 개), `git status --porcelain code ../Demo` 0 줄.
- 단일 S5 표시 파일 `logs/nscale/nscale_s5.start:1` = `869169c64f0658091ab2d755c0cb349a70dbaaf1575a6eddd36f15cc0a0fa33e 68d4d353a24eeb2233007c8225787e03764cade1`; 지금 S5 의 sha256 + 실행 커밋 = `869169c64f0658091ab2d755c0cb349a70dbaaf1575a6eddd36f15cc0a0fa33e 68d4d353a24eeb2233007c8225787e03764cade1` → 같다.

**실행 (`logs/run_nscale.log`)**:
- `L:129` 10-06 08:11 CDT `start eval (git 68d4d353, freeze 2d50dab51629c1731ec41db2f7ed1449ae7ea9d1, fallback 0, K8 run 1, resume 0, S5+HEAD 869169c64f0658091ab2d755c0cb349a70dbaaf1575a6eddd36f15cc0a0fa33e 68d4d353a24eeb2233007c8225787e03764cade1)`
- `L:128` `single-shot marker logs/nscale/nscale_s5.start written (first eval start)`
- `L:251` 10-06 15:06 CDT **`NSCALE_DONE ok=89 fail=0`**.
- 경과 6 h 55 min (`L:129` → `L:251`, 로그 시각의 기록자 산술; 연도 = `date`). §1 비용 행의 CPU 추정 (`reg:162`) 과 나란히 적는다 (§6.1.6).
- rc=0 줄 89 개 (기록자 셈) — `NSCALE_DONE` 의 ok 와 같다.
- ABORT·rc≠0·SKIPPED 줄 0 (기록자 grep).
- runner 로그 머리말 `# run_nscale …` 수: BRB32e4 1, BRNR16B16e4 1, B64e4 1, B128e4 1, B64e4chk 1, B128e4chk 1, B64e4last 1, B128e4last 1, K2B32e4 1, K2B64e4 1, K2B128e4 1, NR16B64e4 1, NR16B64e4chk 1, NR16B64e4last 1, K2NR16B64e4 1, B64e4k8 1; warn/error/traceback/exception 줄 0 개 (기록자 grep, 대소문자 무시). analysis 로그의 `WARNING` 줄 0 개.

**runner 실행 (태그별; `run_<T>` 의 머리말 · `Stage C checkpoint` 줄 · workers 줄 · 첫 `done` 줄의 청크 초 · 끝 줄 `finished in`; 완료 시각 = `L:` 의 `run` 줄)**

| 태그 | 명령 (머리말 줄의 `--cell`·`--snr`·`--n`) | 체크포인트 | 워커 (줄) | 첫 `done` 청크 (줄) | 소요 (줄) | 파일 · 완료 CDT (`L:`) |
|---|---|---|---|---|---|---|
| BRB32e4 | `--cell C2 --n 40 --snr -3` (:1; 머리말 1 개) | `sha256[:16]=035744cbe955984d epoch=966 best_epoch=966 role=best 8x4` (:5) | 1 (:7) | 312 s (:8) | 5.2 min (:9) | 1/1 · 10-06 08:16 CDT (`L:130`) rc=0 |
| BRNR16B16e4 | `--cell C6 --n 40 --snr -3` (:1; 머리말 1 개) | `sha256[:16]=c050d611b2c714a6 epoch=1684 best_epoch=1684 role=best 16x4` (:5) | 1 (:7) | 2072 s (:8) | 34.5 min (:9) | 1/1 · 10-06 08:51 CDT (`L:131`) rc=0 |
| B64e4 | `--cell C2 --n 2560` (:1; 머리말 1 개) | `sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4` (:5) | 192 (:7) | 761 s (:8) | 34.0 min (:456) | 448/448 · 10-06 09:25 CDT (`L:132`) rc=0 |
| B128e4 | `--cell C2 --n 2560` (:1; 머리말 1 개) | `sha256[:16]=ec1c29cdf4eabac7 epoch=866 best_epoch=866 role=best 8x4` (:5) | 192 (:7) | 761 s (:8) | 34.2 min (:456) | 448/448 · 10-06 09:59 CDT (`L:134`) rc=0 |
| B64e4chk | `--cell C2 --n 40 --snr -3` (:1; 머리말 1 개) | `sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4` (:5) | 1 (:7) | 312 s (:8) | 5.2 min (:9) | 1/1 · 10-06 10:05 CDT (`L:136`) rc=0 |
| B128e4chk | `--cell C2 --n 40 --snr -3` (:1; 머리말 1 개) | `sha256[:16]=ec1c29cdf4eabac7 epoch=866 best_epoch=866 role=best 8x4` (:5) | 1 (:7) | 312 s (:8) | 5.2 min (:9) | 1/1 · 10-06 10:10 CDT (`L:137`) rc=0 |
| B64e4last | `--cell C2 --n 2560` (:1; 머리말 1 개) | `sha256[:16]=fa3afcfb84259976 epoch=1237 best_epoch=1217 role=last 8x4` \| … (:5) | 192 (:7) | 736 s (:8) | 33.8 min (:456) | 448/448 · 10-06 10:44 CDT (`L:138`) rc=0 |
| B128e4last | `--cell C2 --n 2560` (:1; 머리말 1 개) | `sha256[:16]=cd6106d493bcbdae epoch=886 best_epoch=866 role=last 8x4` \| … (:5) | 192 (:7) | 735 s (:8) | 33.8 min (:456) | 448/448 · 10-06 11:18 CDT (`L:140`) rc=0 |
| K2B32e4 | `--cell C2 --n 2560 --snr -3 0 3` (:1; 머리말 1 개) | `sha256[:16]=035744cbe955984d epoch=966 best_epoch=966 role=best 8x4` (:5) | 192 (:7) | 139 s (:8) | 2.4 min (:200) | 192/192 · 10-06 11:21 CDT (`L:142`) rc=0 |
| K2B64e4 | `--cell C2 --n 2560 --snr -3 0 3` (:1; 머리말 1 개) | `sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4` (:5) | 192 (:7) | 139 s (:8) | 2.4 min (:200) | 192/192 · 10-06 11:23 CDT (`L:143`) rc=0 |
| K2B128e4 | `--cell C2 --n 2560 --snr -3 0 3` (:1; 머리말 1 개) | `sha256[:16]=ec1c29cdf4eabac7 epoch=866 best_epoch=866 role=best 8x4` (:5) | 192 (:7) | 139 s (:8) | 2.4 min (:200) | 192/192 · 10-06 11:26 CDT (`L:144`) rc=0 |
| NR16B64e4 | `--cell C6 --n 2560` (:1; 머리말 1 개) | `sha256[:16]=001a9e2e2a0feafd epoch=458 best_epoch=458 role=best 16x4` (:5) | 192 (:7) | 2704 s (:8) | 124.7 min (:456) | 448/448 · 10-06 13:31 CDT (`L:145`) rc=0 |
| NR16B64e4chk | `--cell C6 --n 40 --snr -3` (:1; 머리말 1 개) | `sha256[:16]=001a9e2e2a0feafd epoch=458 best_epoch=458 role=best 16x4` (:5) | 1 (:7) | 1222 s (:8) | 20.4 min (:9) | 1/1 · 10-06 13:51 CDT (`L:147`) rc=0 |
| NR16B64e4last | `--cell C6 --n 2560 --snr -3 0 3` (:1; 머리말 1 개) | `sha256[:16]=08feec97841119f7 epoch=478 best_epoch=458 role=last 16x4` \| … (:5) | 192 (:7) | 2384 s (:8) | 46.3 min (:200) | 192/192 · 10-06 14:38 CDT (`L:148`) rc=0 |
| K2NR16B64e4 | `--cell C6 --n 2560 --snr -3 0 3` (:1; 머리말 1 개) | `sha256[:16]=001a9e2e2a0feafd epoch=458 best_epoch=458 role=best 16x4` (:5) | 192 (:7) | 630 s (:8) | 11.0 min (:200) | 192/192 · 10-06 14:49 CDT (`L:149`) rc=0 |
| B64e4k8 | `--cell C2 --n 2560 --snr -3 0 3` (:1; 머리말 1 개) | `sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4` (:5) | 192 (:7) | 624 s (:8) | 11.6 min (:200) | 192/192 · 10-06 15:00 CDT (`L:150`) rc=0 |

(첫 `done` 청크 초는 그 줄에 찍힌 청크 하나의 소요이고, 워커가 동시에 돌므로 첫 시작 청크의 시간은 아니다. 실행 순서 = §1 실행 순서 행: bridge 2 → C2 A·analysis → chk → last·analysis → K2B32e4·K2<T> → C6 A·analysis·chk·last·K2 → B64e4k8.)

**raw (기록자 확인, 단일 프로세스·GPU 숨김; `meta|*`·`run|*` 키만 읽음 — 청크마다 값 집합)**:

| raw | 파일 | `run\|git` | `meta\|ntrain` | `meta\|bstar` · `kron_K` · `ll_val\|<b*>` | `meta\|stagec_ckpt_id` | `meta\|em_sec` | `jobs` · `worker_gb` | §5 대조 |
|---|---|---|---|---|---|---|---|---|
| `raw_BRB32e4` | 1 | 68d4d353 | 320000.0 | kron · 4096 · -5.942083265612076 | sha256[:16]=035744cbe955984d epoch=966 best_epoch=966 role=best 8x4 | 272084.78322577477 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓ |
| `raw_BRNR16B16e4` | 1 | 68d4d353 | 160000.0 | kron · 4096 · 63.1751571838059 | sha256[:16]=c050d611b2c714a6 epoch=1684 best_epoch=1684 role=best 16x4 | 46649.95333504677 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓ |
| `raw_B64e4` | 448 | 68d4d353 | 640000.0 | kron · 4096 · -4.2936152070786635 | sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4 | 83127.26096606255 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_B128e4` | 448 | 68d4d353 | 1280000.0 | kron · 4096 · -3.1746045830106424 | sha256[:16]=ec1c29cdf4eabac7 epoch=866 best_epoch=866 role=best 8x4 | 177597.21678066254 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_B64e4chk` | 1 | 68d4d353 | 640000.0 | kron · 4096 · -4.2936152070786635 | sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4 | 83127.26096606255 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_B128e4chk` | 1 | 68d4d353 | 1280000.0 | kron · 4096 · -3.1746045830106424 | sha256[:16]=ec1c29cdf4eabac7 epoch=866 best_epoch=866 role=best 8x4 | 177597.21678066254 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_B64e4last` | 448 | 68d4d353 | 640000.0 | kron · 4096 · -4.2936152070786635 | sha256[:16]=fa3afcfb84259976 epoch=1237 best_epoch=1217 role=last 8x4 \| … | 83127.26096606255 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_B128e4last` | 448 | 68d4d353 | 1280000.0 | kron · 4096 · -3.1746045830106424 | sha256[:16]=cd6106d493bcbdae epoch=886 best_epoch=866 role=last 8x4 \| … | 177597.21678066254 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_K2B32e4` | 192 | 68d4d353 | 320000.0 | kron · 2048 · -7.792724507139091 | sha256[:16]=035744cbe955984d epoch=966 best_epoch=966 role=best 8x4 | 257842.8704841137 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓ |
| `raw_K2B64e4` | 192 | 68d4d353 | 640000.0 | kron · 2048 · -6.855596311929488 | sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4 | 60047.52908706665 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_K2B128e4` | 192 | 68d4d353 | 1280000.0 | kron · 2048 · -6.175440687470083 | sha256[:16]=ec1c29cdf4eabac7 epoch=866 best_epoch=866 role=best 8x4 | 127206.97145032883 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_NR16B64e4` | 448 | 68d4d353 | 640000.0 | kron · 4096 · 81.9525983268529 | sha256[:16]=001a9e2e2a0feafd epoch=458 best_epoch=458 role=best 16x4 | 241421.51667571068 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_NR16B64e4chk` | 1 | 68d4d353 | 640000.0 | kron · 4096 · 81.9525983268529 | sha256[:16]=001a9e2e2a0feafd epoch=458 best_epoch=458 role=best 16x4 | 241421.51667571068 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_NR16B64e4last` | 192 | 68d4d353 | 640000.0 | kron · 4096 · 81.9525983268529 | sha256[:16]=08feec97841119f7 epoch=478 best_epoch=458 role=last 16x4 \| … | 241421.51667571068 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_K2NR16B64e4` | 192 | 68d4d353 | 640000.0 | kron · 2048 · 75.1325369582494 | sha256[:16]=001a9e2e2a0feafd epoch=458 best_epoch=458 role=best 16x4 | 179685.45542550087 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |
| `raw_B64e4k8` | 192 | 68d4d353 | 640000.0 | kron · 8192 · -2.4856244669792424 | sha256[:16]=f6e4a6b000d35f5a epoch=1217 best_epoch=1217 role=best 8x4 | 135045.38613057137 | (키 없음) · (키 없음) | ntrain ✓, kron_K ✓, ll_val ✓, ckpt sha·role ✓ |

- `run|git` = 실행 커밋 68d4d353: 16/16 raw.
- 수용 (c) 수동 대조 B64e4: A raw `epoch=` ['1217'] · last raw `best_epoch=` ['1217'] → 일치.
- 수용 (c) 수동 대조 B128e4: A raw `epoch=` ['866'] · last raw `best_epoch=` ['866'] → 일치.
- 수용 (c) 수동 대조 NR16B64e4: A raw `epoch=` ['458'] · last raw `best_epoch=` ['458'] → 일치.
- run_manifest (`L:` 의 JSON 줄): BRB32e4 config_hash 2634ef8c910db321 · n_raw_files 1 · git 68d4d353 (`L:151`); BRNR16B16e4 config_hash 33e2658a026c3952 · n_raw_files 1 · git 68d4d353 (`L:154`); B64e4 config_hash 47c86c5b12562624 · n_raw_files 448 · git 68d4d353 (`L:157`); B128e4 config_hash 5217b08e71d1352b · n_raw_files 448 · git 68d4d353 (`L:160`); B64e4chk config_hash 738dc04ed5488bed · n_raw_files 1 · git 68d4d353 (`L:163`); B128e4chk config_hash f5f2148fc6751654 · n_raw_files 1 · git 68d4d353 (`L:166`); B64e4last config_hash 47c86c5b12562624 · n_raw_files 448 · git 68d4d353 (`L:169`); B128e4last config_hash 5217b08e71d1352b · n_raw_files 448 · git 68d4d353 (`L:172`); K2B32e4 config_hash ca97503e9ab19a8f · n_raw_files 192 · git 68d4d353 (`L:175`); K2B64e4 config_hash adccb9590207640a · n_raw_files 192 · git 68d4d353 (`L:178`); K2B128e4 config_hash b4f3b49adfd201ef · n_raw_files 192 · git 68d4d353 (`L:181`); NR16B64e4 config_hash 63f1e3315a109623 · n_raw_files 448 · git 68d4d353 (`L:184`); NR16B64e4chk config_hash 29a427e6eba77c00 · n_raw_files 1 · git 68d4d353 (`L:187`); NR16B64e4last config_hash 2fefb41aa7df6a3f · n_raw_files 192 · git 68d4d353 (`L:190`); K2NR16B64e4 config_hash 2fefb41aa7df6a3f · n_raw_files 192 · git 68d4d353 (`L:193`); B64e4k8 config_hash adccb9590207640a · n_raw_files 192 · git 68d4d353 (`L:196`).
- 가드 보고 B64e4: 발동 줄 7 개 — `C2       -3 M-ours-dscore-C-V0          1853   2560   0.724  2.472e+08` (:18); `C2       +0 M-ours-dscore-C-V0          2279   2560   0.890  4.914e+08` (:19); `C2       +3 M-ours-dscore-C-V0          2430   2560   0.949  1.501e+08` (:20); `C2       +6 M-ours-dscore-C-V0          2428   2560   0.948  2.905e+08` (:21); `C2       +9 M-ours-dscore-C-V0          2400   2560   0.938  5.275e+09` (:22); `C2      +12 M-ours-dscore-C-V0          2250   2560   0.879  4.168e+09` (:23); `C2      +15 M-ours-dscore-C-V0          1780   2560   0.695  1.864e+08` (:24)
- 가드 보고 B128e4: 발동 줄 7 개 — `C2       -3 M-ours-dscore-C-V0          1770   2560   0.691  5.734e+07` (:18); `C2       +0 M-ours-dscore-C-V0          2300   2560   0.898  2.814e+11` (:19); `C2       +3 M-ours-dscore-C-V0          2355   2560   0.920  1.475e+09` (:20); `C2       +6 M-ours-dscore-C-V0          2464   2560   0.963  1.965e+15` (:21); `C2       +9 M-ours-dscore-C-V0          2398   2560   0.937  3.456e+09` (:22); `C2      +12 M-ours-dscore-C-V0          2277   2560   0.889  4.577e+09` (:23); `C2      +15 M-ours-dscore-C-V0          1933   2560   0.755  9.339e+08` (:24)
- 가드 보고 NR16B64e4 (`guard_NR16B64e4:16`): "NO GUARD FIRINGS in this raw set." (`guard_NR16B64e4:19` `not applicable -- no channel estimate, so no Module H path (1): R5-genie`)

**수용 (`<K>_accept.txt` 원문; 로그 줄)**:

| 태그 (게이트) | 원문 | 로그 |
|---|---|---|
| BRB32e4 (bridge → C2 P2·S1) | `ACCEPT: OK -- BRB32e4` (`acc_BRB32e4:1`) / `(f) raw_BRB32e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:199` rc=0 |
| BRNR16B16e4 (bridge → C6 P2) | `ACCEPT: OK -- BRNR16B16e4` (`acc_BRNR16B16e4:1`) / `(f) raw_BRNR16B16e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:200` rc=0 |
| K2B32e4 (Q-K 기준 끝 C2) | `ACCEPT: OK -- K2B32e4` (`acc_K2B32e4:1`) / `(f) raw_K2B32e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:201` rc=0 |
| B64e4 (A: P1·P2·(E); (a)(b)(d)) | `ACCEPT: OK -- B64e4` (`acc_B64e4:1`) / `(f) raw_B64e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:206` rc=0 |
| B64e4chk (chk: P2·(E); (e)) | `ACCEPT: OK -- B64e4chk` (`acc_B64e4chk:1`) / `(f) raw_B64e4chk: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:207` rc=0 |
| B64e4last (last: 보고 전용) | `ACCEPT: OK -- B64e4last` (`acc_B64e4last:1`) / `(f) raw_B64e4last: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:208` rc=0 |
| K2B64e4 (Q-K 새 끝) | `ACCEPT: OK -- K2B64e4` (`acc_K2B64e4:1`) / `(f) raw_K2B64e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:209` rc=0 |
| B128e4 (A: P1·P2·(E); (a)(b)(d)) | `ACCEPT: OK -- B128e4` (`acc_B128e4:1`) / `(f) raw_B128e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:215` rc=0 |
| B128e4chk (chk: P2·(E); (e)) | `ACCEPT: OK -- B128e4chk` (`acc_B128e4chk:1`) / `(f) raw_B128e4chk: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:216` rc=0 |
| B128e4last (last: 보고 전용) | `ACCEPT: OK -- B128e4last` (`acc_B128e4last:1`) / `(f) raw_B128e4last: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:217` rc=0 |
| K2B128e4 (Q-K 새 끝) | `ACCEPT: OK -- K2B128e4` (`acc_K2B128e4:1`) / `(f) raw_K2B128e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:218` rc=0 |
| NR16B64e4 (A: P1·P2·(E); (a)(b)(d)) | `ACCEPT: OK -- NR16B64e4` (`acc_NR16B64e4:1`) / `(f) raw_NR16B64e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:224` rc=0 |
| NR16B64e4chk (chk: P2·(E); (e)) | `ACCEPT: OK -- NR16B64e4chk` (`acc_NR16B64e4chk:1`) / `(f) raw_NR16B64e4chk: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:225` rc=0 |
| NR16B64e4last (last: 보고 전용) | `ACCEPT: OK -- NR16B64e4last` (`acc_NR16B64e4last:1`) / `(f) raw_NR16B64e4last: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:226` rc=0 |
| K2NR16B64e4 (Q-K 새 끝) | `ACCEPT: OK -- K2NR16B64e4` (`acc_K2NR16B64e4:1`) / `(f) raw_K2NR16B64e4: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:227` rc=0 |
| B64e4k8 (보고 전용 K8) | `ACCEPT: OK -- B64e4k8` (`acc_B64e4k8:1`) / `(f) raw_B64e4k8: run\|git ['68d4d353']` (:2) / `ACCEPT (f): OK` (:3) | `L:229` rc=0 |
| K2NR16B16e4 (Q-K 기준 끝 C6; SCALE16e4 기록, 링크) | `ACCEPT: OK -- K2NR16B16e4` (`acc_K2NR16B16e4:1`) | (기록 파일) |

→ **수용 (a)–(k)** (§1 수용 검사 행):
- (a) 격자 완전성 (A 호출의 `--grid`): A 파일의 `grid:` 실패 줄 0 개; K2 호출 (`--cand-dir`) 포함 전체 `grid:` 줄 0 개.
- (b) 태그별 meta (청크 계획·ntrain·b\*·kron_K·ll_val·ckpt sha·role·run\|iters): 위 원문 (실패 줄이 있으면 그 줄).
- (c) 체크포인트: §5 (`prep` 출력) + 위 raw 절의 수동 대조.
- (d) genie 재생 (A 의 `--ref-raw` = 기준 raw): A 파일의 `replay vs` 실패 줄 0 개.
- (e) 재현 (`--ref-arms all`): bridge BRB32e4 통과, BRNR16B16e4 통과; chk B64e4chk 통과, B128e4chk 통과, NR16B64e4chk 통과. **bridge 실패 → 그 셀의 1차는 (T-iv) "수용 실패"** (§1 (e)).
- (f) `run|git` (gitchk): (f) 줄 16 개, 값 = ['68d4d353'] (실행 커밋 68d4d353); `ACCEPT (f): OK` 아닌 파일: 없음.
- (g) b\*·K2·K8 구성: §5 (`S5` PT·K8 줄, `prep` 의 `K2 set b* = kron 2048 … OK`) + 위 raw 절의 `kron_K` (K2 raw 2048, B64e4k8 8192).
- (h) GB′ (보고 전용, 게이트 아님) · (i) D1 게이트 행 · (j) 메모리 (적합 로그 OOM 없음): §5 그대로 (§6.1.5 (c)·§6.1.7).
- (k) 무결성 줄 (보고 전용, 게이트 아님): §6.1.5 (j)·(k).
- 게이트 (§1 수용 검사 행 끝): P1 = A (B64e4 통과, B128e4 통과, NR16B64e4 통과); P2·2차 (S) = 새 A + 새 chk + 기준 bridge (C2 통과, C6 통과); S2 = 두 새 점의 A·chk (통과); (E) = 새 A + chk (통과); Q-K = 추가로 두 끝의 K2 (기준 C6 K2 = 기록 `K2NR16B16e4_accept.txt` 통과).

#### 6.1.1 P1 점별 (새 점마다; §2.1, 표 B `M-ours-bstar → M-ours-dscore-C-V1`, 판정점 = 앵커 b\* 자동)

| 점 (태그) | 게이트 (S5) | 판정점 | 점별 a:b (p) | pooled (p) | 가드 · 유의 | AUTO-LABEL (도우미) | §2.1 기록 | SNR@0.1 격차 b\* − V1 | 출처 |
|---|---|---|---|---|---|---|---|---|---|
| B64e4 (C2, N′ 6.4e5) | PASS (`S5:5`) | −3/+0/+3 | -3 dB 269:48 (1.9e-38) · +0 dB 98:16 (1.5e-15) · +3 dB 27:6 (0.00032) | 394:70 (8e-56) | POWERED, second arm fewer 3/3, first 0/3 (`significant`) | `통과 (POWERED, second arm fewer >= 2/3)  (POWERED=True, second 3/3, first 0/3)` (:8) | **"동일예산 우위가 N′ = 6.4e5 에서도 유지"** (`reg:176`) — arm 결과, 예산 곡선의 점. 헤드라인 불변 + "격자 끝 (상한)" 캐비엇 (b\* = kron 4096, S5) | +1.24 dB  [90% paired bootstrap +1.06, +1.44; censored replicates 0%] | `P1_B64e4:2–7` = `tab_B64e4:368–373` |
| B128e4 (C2, N′ 1.28e6) | PASS (`S5:6`) | −3/+0/+3 | -3 dB 274:61 (2.3e-33) · +0 dB 87:20 (3.8e-11) · +3 dB 30:9 (0.0011) | 391:90 (9.5e-46) | POWERED, second arm fewer 3/3, first 0/3 (`significant`) | `통과 (POWERED, second arm fewer >= 2/3)  (POWERED=True, second 3/3, first 0/3)` (:8) | **"동일예산 우위가 N′ = 1.28e6 에서도 유지"** (`reg:176`) — arm 결과, 예산 곡선의 점. 헤드라인 불변 + "격자 끝 (상한)" 캐비엇 (b\* = kron 4096, S5) | +1.10 dB  [90% paired bootstrap +0.92, +1.30; censored replicates 0%] | `P1_B128e4:2–7` = `tab_B128e4:368–373` |
| NR16B64e4 (C6, N′ 6.4e5) | UNGATED (`S5:8`) | −3/+0/+3 | -3 dB 119:13 (1.3e-22) · +0 dB 43:6 (5.7e-08) · +3 dB 27:4 (3.4e-05) | 189:23 (1.2e-33) | POWERED, second arm fewer 3/3, first 0/3 (`significant`) | `(i)  (POWERED=True, second 3/3, first 0/3)` (:8) | (i) **"C6 동일예산 우위가 N′ = 6.4e5 에서도 유지 (기하 축 측정, UNGATED)"** — 회수율 대역: R(−3 dB) = 0.779 [90% 0.707, 0.850] (b\* 158 · V1 52 · genie 22, n=2560; `rec_NR16B64e4:2`; 기록자 산술 정확값 0.7794117647058824) → **"기하 효과 대부분 유지"** (`reg:150`) | n/a (<=  -3 vs <=  -3) — extend the SNR grid | `P1_NR16B64e4:2–7` = `tab_NR16B64e4:305–310` |

- C2 의 "통과" = 출력 줄 `power guard … -> POWERED` 이고 `second arm fewer failures at k/3 points` 의 k ≥ 2 (`reg:150`); `significant` 토큰은 판정 기준이 아니다. C6 라벨 (i)–(iv) 는 §2.1 C6 표.
- (ii)(iii)(iv) 어디에도 "소예산 효과" 문구를 만들지 않는다 — 그 문구는 회수율 대역에서만 나온다. 어느 결과도 헤드라인·C2 판정·기존 C6 기록을 바꾸지 않는다 (§2.1).

**필수 대조군 `M-ours-bstar → M-ours-bstar-scalar` (보고만, 같은 형식)**:
- B64e4 (`P1_B64e4:9–14`): 판정점 −3/+0/+3, 63:84 (0.099) · 26:57 (0.00088) · 7:21 (0.013), pooled 96:162 (4.8e-05), POWERED, `second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points -> significant`; SNR@0.1 격차 -0.33 dB  [90% paired bootstrap -0.49, -0.18; censored replicates 0%].
- B128e4 (`P1_B128e4:9–14`): 판정점 −3/+0/+3, 52:87 (0.0038) · 26:50 (0.0079) · 9:12 (0.66), pooled 87:149 (6.6e-05), POWERED, `second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points -> significant`; SNR@0.1 격차 -0.27 dB  [90% paired bootstrap -0.41, -0.14; censored replicates 0%].
- NR16B64e4 (`P1_NR16B64e4:9–14`): 판정점 −3/+0/+3, 29:87 (6.5e-08) · 15:34 (0.0094) · 9:13 (0.52), pooled 53:134 (2.8e-09), POWERED, `second arm fewer failures at 0/3 points, first arm fewer failures at 2/3 points -> significant`; SNR@0.1 격차 n/a (<=  -3 vs <=  -3) — extend the SNR grid.

#### 6.1.2 P2 1차 (짝 추세 ΔR, Holm m = 2; §1 P2·다중성·가드 행, §2.2)

- 대비: ΔR_C2 = R(1.28e6) − R(3.2e5) (`FALLBACK 0`, `S5:4`), ΔR_C6 = R(6.4e5) − R(1.6e5); 고정 SNR −3/0/+3 dB 합, `frontier_ci.py --paired` (B 2000, seed 20260926).

| 셀 | R(새) [90%] (b\* · V1 · genie) | R(기준) [90%] | ΔR [90% paired] | ΔR [95% paired] | 부트스트랩 p | 정의 불가 복제 | 출처 |
|---|---|---|---|---|---|---|---|
| C2 | 0.453 [0.412, 0.493] (`raw_B128e4`: 789 · 488 · 125) | 0.495 [0.457, 0.532] (`raw_B32e4`: 836 · 484 · 125) | -0.042 [-0.076, -0.008] | -0.042 [-0.082, -0.001] | 0.0440 | 0 | `P2_C2:3–5`; `L:231` rc=0 |
| C6 | 0.779 [0.721, 0.836] (`raw_NR16B64e4`: 253 · 87 · 40) | 0.823 [0.772, 0.874] (`raw_NR16B16e4`: 277 · 82 · 40) | -0.043 [-0.098, +0.010] | -0.043 [-0.111, +0.020] | 0.1830 | 0 | `P2_C6:3–5`; `L:232` rc=0 |

**가드 점검 (§1 가드 행; 셀마다)**:
- C2: R1: ΣF_b\* 789 > ΣF_g 125, ΣF_g 125 < ΣF_V1 488 (`P2_C2:3`); R2: ΣF_b\* 836 > ΣF_g 125, ΣF_g 125 < ΣF_V1 484 (`P2_C2:4`); 정의 불가 복제 0 / B=2000 (≤ 5 %; `P2_C2:5`) → **(T-iv) 없음**.
- C6: R1: ΣF_b\* 253 > ΣF_g 40, ΣF_g 40 < ΣF_V1 87 (`P2_C6:3`); R2: ΣF_b\* 277 > ΣF_g 40, ΣF_g 40 < ΣF_V1 82 (`P2_C6:4`); 정의 불가 복제 0 / B=2000 (≤ 5 %; `P2_C6:5`) → **(T-iv) 없음**.

**Holm 순서 (§1 다중성 행)**: p_C2 = 0.0440, p_C6 = 0.1830 → **C2 첫째 (95 % CI), C6 둘째 (90 % CI)** (p 가 작은 쪽이 첫째, 동률이면 C2 첫째, (T-iv) 는 항상 둘째; `reg:152`).
- **C2 (첫째, 95 %)**: -0.042 [95% -0.082, -0.001] → **(T−)**; 도우미 `(T−)` (`P2_holm:2`) 같음.
- **C6 (둘째, 90 %)**: -0.043 [90% -0.098, +0.010] → **(T0)**; 도우미 `(T0)` (`P2_holm:3`) 같음.

**1차 라벨 (§2.2 문구 그대로)과 한정어 (Q-OP·Q-K; (T±) 일 때 반드시 붙임, (T0) 에서는 줄만 보고)**:
- **C2 — (T−)**: "N′ 를 3.2e5 → 1.28e6 (4 배) 로 늘릴 때 V1 의 genie 격차 회수율 (b\* 대비 상대 격차) 이 작아진다 (C2, 같은 테스트 시행 짝 비교, b\* 판정점 −3/0/+3 dB, attempt 1 · 학습 집합 1 개 (공개 3·5), D1 형제 게이트 기준 PASS / 새 PASS)" + G_N (b\* = 등록 프로토콜의 GMM — full K ≤ 512 (κ 4 개), kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 상한 4096 대비 N′/K: 3.2e5 78, 1.28e6 312; 격자 끝·tol 정지 점: 3.2e5 `B32e4` 격자 끝 kron 4096 (상한) (`results/gmm_fits_D2_B32e4/fit_S2_Nr8_kronK4096_n320000.npz` n_iter/it_best; §0.4 `reg:115`); 1.28e6 `B128e4` 격자 끝 kron 4096 (상한) (`prep:56`, `S5:6`)) + Q-OP **'[한정어 판정 불가: 비짝 CI 폭 (L⁰ = (T0))]'** + Q-K **'[한정어 판정 불가: 비짝 CI 폭 (L⁰ = (T0))]'** (§2.2 L⁰ 규칙).
  - L⁰ (실행 (a) 의 비짝 `R1 - R2` `--level` 줄, `qk_C2_L95:6`): -0.042 [95% unpaired -0.107, +0.024], p 0.2270 → **L⁰ = (T0)**
  - 실행 (a) `R1+` (`qk_C2_L95:10`): `raw_B128e4 C2 kron_K 4096  K/2 raw raw_K2B128e4 kron_K 2048  b*(K/2) 828  dF = +39  c_K = 4.6065  SigmaF+ = 609.347  R+ = 0.251  [90% -0.027, 0.417]  SigmaF+ <= SigmaF_g in 0.0% of replicates`
  - 실행 (a) `R2+` (`qk_C2_L95:11`): `raw_B32e4 C2 kron_K 4096  K/2 raw raw_K2B32e4 kron_K 2048  b*(K/2) 846  dF = +10  c_K = 2.02137  SigmaF+ = 815.786  R+ = 0.480  [90% 0.414, 0.525]  SigmaF+ <= SigmaF_g in 0.0% of replicates`
  - 실행 (a) `R1+ - R2+` (`qk_C2_L95:12`): -0.230 [95% unpaired -0.591, -0.021], p 0.0260, undefined 0 → L⁺ = (T−)
  - 실행 (b) `R1+` (`qk_C2_L95_qkN:10`): `raw_B128e4 C2 kron_K 4096  K/2 raw raw_K2B128e4 kron_K 2048  b*(K/2) 828  dF = +39  c_K = 4.6065  SigmaF+ = 609.347  R+ = 0.251  [90% -0.027, 0.417]  SigmaF+ <= SigmaF_g in 0.0% of replicates`
  - 실행 (b) `R1+ - R2+` (`qk_C2_L95_qkN:11`): -0.245 [95% unpaired -0.609, -0.051], p 0.0050, undefined 0 → L⁺ = (T−)
  - 실행 (c) `R2+` (`qk_C2_L95_qkB:10`): `raw_B32e4 C2 kron_K 4096  K/2 raw raw_K2B32e4 kron_K 2048  b*(K/2) 846  dF = +10  c_K = 2.02137  SigmaF+ = 815.786  R+ = 0.480  [90% 0.414, 0.525]  SigmaF+ <= SigmaF_g in 0.0% of replicates`
  - 실행 (c) `R1+ - R2+` (`qk_C2_L95_qkB:11`): -0.027 [95% unpaired -0.097, +0.066], p 0.5930, undefined 0 → L⁺ = (T0)
  - R\*1 (`qk_C2_L95:14`): `raw_B128e4 C2 grid ['-3', '+0', '+3', '+6', '+9', '+12', '+15'] n=2560  s* = +0.53 dB  B_V1(s*) = 0.0286  B_g(s*) = 0.0089  R* = 0.519  [95% 0.410, 0.618]  undefined replicates 0.0% (lo 0, hi 0, B_g>=t 0)`
  - R\*2 (`qk_C2_L95:15`): `raw_B32e4 C2 grid ['-3', '+0', '+3', '+6', '+9', '+12', '+15'] n=2560  s* = +0.76 dB  B_V1(s*) = 0.0246  B_g(s*) = 0.0083  R* = 0.610  [95% 0.522, 0.695]  undefined replicates 0.0% (lo 0, hi 0, B_g>=t 0)`
  - L\* = R\*1 − R\*2 (`qk_C2_L95:16`): -0.091 [95% unpaired -0.224, +0.031], p 0.1720, undefined 0
- **C6 — (T0)**: **"판정하지 못함 (방향 없음)"**. 동등성의 증거가 아니다; (T0) 은 이 설계의 예상 결과다 (§0.3 검정력) — 그것이 "예산과 무관하다" 의 증거가 아니다 (`reg:222`). 한정어는 붙이지 않는다 ((T±) 일 때만; §2.2) — 아래 줄은 보고만.
  - L⁰ (실행 (a) 의 비짝 `R1 - R2` `--level` 줄, `qk_C6_L90:6`): -0.043 [90% unpaired -0.123, +0.031], p 0.3450 → **L⁰ = (T0)**
  - 실행 (a) `R1+` (`qk_C6_L90:10`): `raw_NR16B64e4 C6 kron_K 4096  K/2 raw raw_K2NR16B64e4 kron_K 2048  b*(K/2) 254  dF = +1  c_K = 2.33983  SigmaF+ = 250.66  R+ = 0.777  [90% 0.667, 0.833]  SigmaF+ <= SigmaF_g in 0.0% of replicates`
  - 실행 (a) `R2+` (`qk_C6_L90:11`): `raw_NR16B16e4 C6 kron_K 4096  K/2 raw raw_K2NR16B16e4 kron_K 2048  b*(K/2) 272  dF = -5  c_K = 1  SigmaF+ = 277  R+ = 0.823  [90% 0.767, 0.872]  SigmaF+ <= SigmaF_g in 0.0% of replicates  [K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = -5)]`
  - 실행 (a) `R1+ - R2+` (`qk_C6_L90:12`): -0.046 [90% unpaired -0.161, +0.033], p 0.3110, undefined 0 → L⁺ = (T0)
  - 실행 (b) `R1+` (`qk_C6_L90_qkN:10`): `raw_NR16B64e4 C6 kron_K 4096  K/2 raw raw_K2NR16B64e4 kron_K 2048  b*(K/2) 254  dF = +1  c_K = 2.33983  SigmaF+ = 250.66  R+ = 0.777  [90% 0.667, 0.833]  SigmaF+ <= SigmaF_g in 0.0% of replicates`
  - 실행 (b) `R1+ - R2+` (`qk_C6_L90_qkN:11`): -0.046 [90% unpaired -0.163, +0.025], p 0.2770, undefined 0 → L⁺ = (T0)
  - 실행 (c) `R2+` (`qk_C6_L90_qkB:10`): `raw_NR16B16e4 C6 kron_K 4096  K/2 raw raw_K2NR16B16e4 kron_K 2048  b*(K/2) 272  dF = -5  c_K = 1  SigmaF+ = 277  R+ = 0.823  [90% 0.767, 0.872]  SigmaF+ <= SigmaF_g in 0.0% of replicates  [K 상한 강건 (K/2 가 더 낫지 않음, ΔF_K = -5)]`
  - 실행 (c) `R1+ - R2+` (`qk_C6_L90_qkB:11`): -0.043 [90% unpaired -0.121, +0.036], p 0.3830, undefined 0 → L⁺ = (T0)
  - R\*1 (`qk_C6_L90:14`): `raw_NR16B64e4 C6 grid ['-3', '+0', '+3', '+6', '+9', '+12', '+15'] n=2560  s* = -2.35 dB  B_V1(s*) = 0.0170  B_g(s*) = 0.0072  R* = 0.771  [90% 0.708, 0.835]  undefined replicates 0.4% (lo 9, hi 0, B_g>=t 0)`
  - R\*2 (`qk_C6_L90:15`): `raw_NR16B16e4 C6 grid ['-3', '+0', '+3', '+6', '+9', '+12', '+15'] n=2560  s* = -2.01 dB  B_V1(s*) = 0.0150  B_g(s*) = 0.0066  R* = 0.806  [90% 0.752, 0.860]  undefined replicates 0.0% (lo 0, hi 0, B_g>=t 0)`
  - L\* = R\*1 − R\*2 (`qk_C6_L90:16`): -0.035 [90% unpaired -0.115, +0.049], p 0.4812, undefined 9
- 기준 C2 끝의 c_K = 2.02 는 이미 알려진 값이다 (공개 2; `reg:207`). Q-K 는 1차에만 붙이고 2차에는 붙이지 않는다.

#### 6.1.3 2차 (측정, 90 %, 보정 없음; §1 2차 행, §2.2 (E)·§2.3)

- **S1 (3.2e5→6.4e5)**: R1 0.477 [0.438, 0.515] (`raw_B64e4`: 804 · 480 · 125), R2 0.495 (`raw_B32e4`), ΔR -0.018 [90% -0.050, +0.016] (95 % 보고 [-0.057, +0.023]), p 0.3780, undefined 0 (`S1_C2:3–5`) → **"C2 3.2e5→6.4e5 판정하지 못함"**.
- **S2 (6.4e5→1.28e6)**: R1 0.453 [0.412, 0.493] (`raw_B128e4`: 789 · 488 · 125), R2 0.477 (`raw_B64e4`), ΔR -0.024 [90% -0.060, +0.011] (95 % 보고 [-0.066, +0.018]), p 0.2610, undefined 0 (`S2_C2:3–5`) → **"C2 6.4e5→1.28e6 판정하지 못함"**.
- 요약 문구 "단조 증가/감소" 는 두 단계가 모두 같은 방향일 때만 — 해당 없음.
- **(E) 데이터 효율** (`eff_C2:4–6`): A = `raw_B128e4` M-ours-bstar SNR@0.1 -1.12 dB [90% -1.30, -0.92; censored 0.0%], B = `raw_B16e4k` M-ours-dscore-C-V1 -2.23 dB; Δ = A − B = +1.11 dB [90% +0.86, +1.36] (95 % 보고 [+0.81, +1.42]), p 0.0000, censored 0.0% → **"C2 에서 N′ = 1.6e5 로 학습한 V1 (D1 형제 게이트 PASS 레시피, 헤드라인 legacy-last 가중치) 이 8 배의 데이터로 적합한 b\* (N′ = 1.28e6) 보다 SNR@0.1 이 1.11 dB 낮다 (같은 테스트 시행, raw 사이 비짝 90 % CI)"** + G_N (b\* = 등록 프로토콜의 GMM — full K ≤ 512 (κ 4 개), kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 상한 4096 대비 N′/K: 1.28e6 312; 격자 끝·tol 정지 점: 1.28e6 `B128e4` 격자 끝 kron 4096 (상한) (`prep:56`, `S5:6`)); `L:248` rc=0.
- (R) C6 회수율 대역은 P1 C6 기록의 일부 (§6.1.1).

#### 6.1.4 합성 문장 S_N (원고용; §2.2 S_N — 조건은 동결 때 고정)

- **C2** 점 집합 = `FALLBACK 0` → {1e4, 4e4, 1.6e5, 3.2e5, 6.4e5, 1.28e6} (n = 6, 128 배); 기준점 4 개는 기록값으로 '통과' 고정 (`reg:209`); 새 점: 모두 통과.
  - **S_N (C2) 성립**: "D2 C2 에서 동일예산 표 B `b* → V1` 이 N′ = 1e4 … 1.28e6 (128 배) 의 등록된 모든 예산 점에서 '통과' (C6 의 (i) 에 해당) 이다 (1e4·4e4 는 D1 형제 게이트 FAIL = 예산 축 측정, 1.6e5·3.2e5 는 PASS 레시피, 새 점은 §5 게이트대로; 게이트 FAIL 인 새 점은 표 B 가 통과여도 '예산 축 측정' 으로 표기하고 arm 주장에는 쓰지 않는다 (§2.1 FAIL 행))" + G_N (새 점 몫: (b\* = 등록 프로토콜의 GMM — full K ≤ 512 (κ 4 개), kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 상한 4096 대비 N′/K: 6.4e5 156, 1.28e6 312; 격자 끝·tol 정지 점: 6.4e5 `B64e4` 격자 끝 kron 4096 (상한) (`prep:20`, `S5:5`); 1.28e6 `B128e4` 격자 끝 kron 4096 (상한) (`prep:56`, `S5:6`))) **[판단 필요: S_N 의 G_N 목록 — 새 점 몫은 아래, 1e4·4e4·1.6e5·3.2e5 의 격자 끝·tol 정지는 §0.1 표·§0.4 에서 옮길 것]**.
- **C6**: `NR16B64e4` = (i) → **S_N (C6) 성립**: "D2 C6 에서 N′ = 1e4 … 6.4e5 (64 배) 의 모든 예산 점에서 (i) (UNGATED 측정)" + 회수율 대역: R(−3 dB) = 0.779 [90% 0.707, 0.850] (b\* 158 · V1 52 · genie 22, n=2560; `rec_NR16B64e4:2`; 기록자 산술 정확값 0.7794117647058824) → **"기하 효과 대부분 유지"** (`reg:150`) + G_N (b\* = 등록 프로토콜의 GMM — full K ≤ 512 (κ 4 개), kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 상한 4096 대비 N′/K: 6.4e5 156; 격자 끝·tol 정지 점: 6.4e5 `NR16B64e4` 격자 끝 kron 4096 (상한)·tol 정지 (274/260) (`prep:89`, `S5:8`)) **[판단 필요: S_N (C6) G_N 의 1e4·1.6e5 몫 (§0.2 표)]**.
- **집계 (§2.4 다중성 문장 그대로, `reg:224`)**: 등록 1차 검정은 2 개 (Holm) 다. P1 점별 판정 3 개는 각자 독립된 기존 규칙 (보정 없음, 선례), 2차·한정어는 새 가설이 아니다.

#### 6.1.5 보고 전용 (§1 보고 전용 행; 라벨에 쓰지 않음)

(a) **예산 곡선 (기준점 행 = §0.1·§0.2 표 그대로 옮김; 새 점 = 이 실행)**:

| 셀 · N′ (raw, 가중치) | b\* | b\* −3 dB | V1 −3 dB | 표 B b\*→V1 pooled | SNR@0.1 격차 [90%] | D1 게이트 | **R** [90% paired] (ΣF b\* / V1 / genie) | R(−3 dB) [90%] | 출처 |
|---|---|---|---|---|---|---|---|---|---|
| C2 1e4 (`raw_B1e4`, last-EMA) | kron 512 (내부) | 0.252 | 0.145 | 502:72 | — | FAIL (GC 0.243) | 0.540 (921 / 491 / 125) [0.506, 0.576] | — | `reg:80` |
| C2 4e4 (`raw_B4e4k`, last-EMA) | kron 2048 (격자 끝) | 0.248 | 0.145 | 459:79 | — | FAIL (GC 0.167) | 0.518 (859 / 479 / 125) [0.481, 0.554] | — | `reg:81` |
| C2 1.6e5 (`raw_B16e4k`, legacy-last **헤드라인**) | kron 1024 (끝일 수 있음) | 0.243 | 0.145 | 454:78 | — | PASS (GC 0.0999) | 0.509 (864 / 488 / 125) [0.470, 0.544] | — | `reg:82` |
| C2 3.2e5 (`raw_B32e4`, `_best` 035744cbe955984d) | kron 4096 (격자 끝, 사용자 멈춤) | 0.238 | 0.146 | 421:69 | — | PASS (GC 0.0937) | **0.495** (836 / 484 / 125) [0.457, 0.532] | — | `reg:83` |
| C2 3.2e5 (`raw_B32e4last`, last-EMA) | 같음 | 0.238 | 0.144 | 418:71 | — | PASS | (보고 전용) | — | `reg:84` |
| C6 1e4 (`raw_NR16run2`, last-EMA) | kron 128 (내부) | (207 / 52 / 22; 335 / 82 / 40) | | 266:13 (i) | — | UNGATED | 0.858 [0.818, 0.899] | 0.838 [0.781, 0.892] | `reg:94` |
| C6 1.6e5 (`raw_NR16B16e4`, **§3d 시행 2 (fb2)** `_best` c050d611b2c714a6) | kron 4096 (격자 끝, 사용자 멈춤; §6.5 tol 정지 캐비엇) | (184 / 53 / 22; 277 / 82 / 40) | | 213:18 (i) | — | UNGATED | **0.823** [0.772, 0.874] | 0.809 [0.747, 0.870] | `reg:95` |
| C2 6.4e5 (`raw_B64e4`, `_best` f6e4a6b000d35f5a) | kron 4096 (`S5:5`) | 0.231 (0.215, 0.248) | 0.145 (0.131, 0.159) | 394:70 | +1.24 dB  [90% paired bootstrap +1.06, +1.44; censored replicates 0%] | PASS | 0.477 [0.439, 0.515] (804 / 480 / 125) | 0.438 [0.395, 0.483] | `tab_B64e4:70` `tab_B64e4:72` `tab_B64e4:368–373` `rec_B64e4:2` `rec_B64e4:8` |
| C2 6.4e5 (`raw_B64e4last`, last-EMA fa3afcfb84259976) | kron 4096 (`S5:5`) | 0.231 (0.215, 0.248) | 0.146 (0.133, 0.161) | 397:67 | +1.28 dB  [90% paired bootstrap +1.11, +1.48; censored replicates 0%] | PASS | 0.486 [0.448, 0.524] (804 / 474 / 125) | 0.429 [0.386, 0.473] | `tab_B64e4last:70` `tab_B64e4last:72` `tab_B64e4last:368–373` `rec_B64e4last:2` `rec_B64e4last:5` |
| C2 1.28e6 (`raw_B128e4`, `_best` ec1c29cdf4eabac7) | kron 4096 (`S5:6`) | 0.228 (0.212, 0.244) | 0.145 (0.131, 0.159) | 391:90 | +1.10 dB  [90% paired bootstrap +0.92, +1.30; censored replicates 0%] | PASS | 0.453 [0.413, 0.493] (789 / 488 / 125) | 0.429 [0.382, 0.477] | `tab_B128e4:70` `tab_B128e4:72` `tab_B128e4:368–373` `rec_B128e4:2` `rec_B128e4:8` |
| C2 1.28e6 (`raw_B128e4last`, last-EMA cd6106d493bcbdae) | kron 4096 (`S5:6`) | 0.228 (0.212, 0.244) | 0.144 (0.131, 0.158) | 389:77 | +1.17 dB  [90% paired bootstrap +0.99, +1.37; censored replicates 0%] | PASS | 0.470 [0.429, 0.509] (789 / 477 / 125) | 0.431 [0.385, 0.478] | `tab_B128e4last:70` `tab_B128e4last:72` `tab_B128e4last:368–373` `rec_B128e4last:2` `rec_B128e4last:5` |
| C6 6.4e5 (`raw_NR16B64e4`, `_best` 001a9e2e2a0feafd) | kron 4096 (`S5:8`) | 0.062 (0.053, 0.072) | 0.020 (0.016, 0.027) | 189:23 | n/a (<=  -3 vs <=  -3) — extend the SNR grid | UNGATED | 0.779 [0.722, 0.836] (253 / 87 / 40) | 0.779 [0.707, 0.850] | `tab_NR16B64e4:70` `tab_NR16B64e4:71` `tab_NR16B64e4:305–310` `rec_NR16B64e4:2` `rec_NR16B64e4:8` |
| C6 6.4e5 (`raw_NR16B64e4last`, last-EMA 08feec97841119f7) | kron 4096 (`S5:8`) | — | — | n/a (analysis 미실행) | — | UNGATED | 0.793 [0.741, 0.845] (253 / 84 / 40) | 0.779 [0.711, 0.847] | `rec_NR16B64e4last:2` `rec_NR16B64e4last:5` |

(기준점 행의 칸 이름은 §0.1/§0.2 표의 칸을 옮긴 것이다 (§0.2 의 −3 dB 칸은 실패 수 원문). b\* −3 dB·V1 −3 dB = `tab_<T>` 표 A 의 BLER (95% Wilson). R 의 CI 는 `recovery_ci` (paired); frontier 의 R1 CI 와 셋째 자리가 다를 수 있다.)
- SNR@0.1 (dB; `tab_<T>` 의 SNR@BLER 0.1 표, '<=x'·'>x' 는 격자 밖 그대로): B64e4 b\* -1.00 (:199) · V1 -2.24 (:201) · genie <=  -3 (:205); B128e4 b\* -1.12 (:199) · V1 -2.22 (:201) · genie <=  -3 (:205); NR16B64e4 b\* <=  -3 (:175) · V1 <=  -3 (:176) · genie <=  -3 (:178).

(b) **GMM ll 사다리 (`prep` = §5; 병합 ll_val, 선택 재시작의 정지·재시드·sec·경로)**:
- **B64e4** (`prep:3`–): kron 16: -38.77681721356206, 32: -33.018309250539545, 64: -27.50016283258215, 128: -22.409260318178628, 256: -17.84624845006982, 512: -13.876738342540357, 1024: -10.155676697271073, 2048: -6.855596311929488, 4096: -4.2936152070786635; full 16: -38.337809223956114, 32: -31.360194545727325, 64: -24.968339135970076, 128: -19.41851503605083, 256: -14.2999221836327, 512: -9.430325411871934 (`prep:6–20`); Δll(4096 − 2048) = 2.5619811048508243, Δll(2048 − 1024) = 3.3000803853415848 (기록자 산술, Python float); `Q-K: r 0.7763389995682298 -> c_K 3.4710521640765846;  K2 set b* = kron 2048 -6.855596311929488 -> kron 2048 OK` (`prep:23`); kron 4096 재시드 898, 정지 patience (381/340), 경로 `batched [1.0, 1.0, 1.0]`, sec 23080 (`prep:20`); 정지 사유 수 (병합 15): cap500 1, patience 9, tol 5.
  - 학습 (구간 규칙, `prep:28`): 구간 2 (학습 1, GB′ 1), 최종 `# done        : 1237 epochs, stopped_by=patience, aborted=False, best val 3.474525e-01 @ epoch 1217, wall 58319.3 s, 47.146 s/epoch`, 학습 초 = 학습 구간 wall 합 58319.3 s.
  - em_sec (raw `meta|em_sec`): 83127.26096606255.
- **B128e4** (`prep:39`–): kron 16: -39.07301514539034, 32: -32.818560665752244, 64: -27.550026199512192, 128: -22.558353349846154, 256: -17.88905884302987, 512: -13.561779664999273, 1024: -9.827712154376806, 2048: -6.175440687470083, 4096: -3.1746045830106424; full 16: -38.394635940839116, 32: -31.14923147028535, 64: -24.97485412554862, 128: -19.259266682926224, 256: -13.999289922047081, 512: -8.81302556797323 (`prep:42–56`); Δll(4096 − 2048) = 3.0008361044594403, Δll(2048 − 1024) = 3.6522714669067238 (기록자 산술, Python float); `Q-K: r 0.8216355579397788 -> c_K 4.606498629712138;  K2 set b* = kron 2048 -6.175440687470083 -> kron 2048 OK` (`prep:59`); kron 4096 재시드 36, 정지 patience (361/320), 경로 `batched [1.0, 1.0, 1.0]`, sec 50390 (`prep:56`); 정지 사유 수 (병합 15): cap500 1, patience 11, tol 3.
  - 학습 (구간 규칙, `prep:64`): 구간 2 (학습 1, GB′ 1), 최종 `# done        : 886 epochs, stopped_by=patience, aborted=False, best val 3.444063e-01 @ epoch 866, wall 85537.8 s, 96.544 s/epoch`, 학습 초 = 학습 구간 wall 합 85537.8 s.
  - em_sec (raw `meta|em_sec`): 177597.21678066254.
- **NR16B64e4** (`prep:72`–): kron 16: -29.06045392700477, 32: -9.48879710732886, 64: 8.487419209725475, 128: 24.665073213419703, 256: 39.733133914797065, 512: 52.92209341584101, 1024: 65.39771233397857, 2048: 75.1325369582494, 4096: 81.9525983268529; full 16: -29.321347143757038, 32: -9.806996983806753, 64: 6.699283115944112, 128: 21.624390562492614, 256: 33.878036491600334, 512: 40.77121185010288 (`prep:75–89`); Δll(4096 − 2048) = 6.82006136860349, Δll(2048 − 1024) = 9.734824624270829 (기록자 산술, Python float); `Q-K: r 0.7005838966630933 -> c_K 2.339833725892784;  K2 set b* = kron 2048 75.1325369582494 -> kron 2048 OK` (`prep:92`); kron 4096 재시드 30032, 정지 tol (274/260), 경로 `batched [1.0, 1.0, 1.0]`, sec 61736 (`prep:89`); 정지 사유 수 (병합 15): cap500 5, patience 2, tol 8.
  - 학습 (구간 규칙, `prep:97`): 구간 2 (학습 1, GB′ 1), 최종 `# done        : 478 epochs, stopped_by=patience, aborted=False, best val 1.768667e-01 @ epoch 458, wall 18772.8 s, 39.274 s/epoch`, 학습 초 = 학습 구간 wall 합 18772.8 s.
  - em_sec (raw `meta|em_sec`): 241421.51667571068.

(c) **GB′ (재실행본, 보고 전용; `prep`)**:
- B64e4: `GB' csv: gmm_ntrain 640000 equal_budget True kron K 4096 ratio min/max/median 0.451443/0.879592/0.514538 worst_excess -0.120408` (`prep:31`); `GB' npz results/d2_gbprime_N640000_a1.npz: newer than the kron 4096 merge: True` (`prep:33`); `gbp_B64e4.log: [d2sx] GMM b* = kron (kron K=4096) @N=640000 \| diff/gmm min 0.4514 max 0.8796 median 0.5145 \| equal_budget=True` (`prep:32`); npz `results/d2_gbprime_N640000_a1.npz` 의 비 nmse_model/nmse_gmm: min 0.451443 · max 0.879592 · median 0.514538, worst excess (= max − 1) -0.120408 (기록자 산술).
- B128e4: `GB' csv: gmm_ntrain 1280000 equal_budget True kron K 4096 ratio min/max/median 0.447127/0.877990/0.513312 worst_excess -0.122010` (`prep:67`); `GB' npz results/d2_gbprime_N1280000_a1.npz: newer than the kron 4096 merge: True` (`prep:69`); `gbp_B128e4.log: [d2sx] GMM b* = kron (kron K=4096) @N=1280000 \| diff/gmm min 0.4471 max 0.8780 median 0.5133 \| equal_budget=True` (`prep:68`); npz `results/d2_gbprime_N1280000_a1.npz` 의 비 nmse_model/nmse_gmm: min 0.447127 · max 0.877990 · median 0.513312, worst excess (= max − 1) -0.122010 (기록자 산술).
- NR16B64e4: `GB' npz results/d2_gbprime_NR16_N640000_a1.npz: newer than the kron 4096 merge: True` (`prep:99`); `gbp_NR16B64e4.log: [nr16] GMM b* = kron (kron K=4096) @N=640000 \| diff/gmm min 0.2728 max 0.5170 median 0.2913 \| equal_budget=True` (`prep:98`); npz `results/d2_gbprime_NR16_N640000_a1.npz` 의 비 nmse_model/nmse_gmm: min 0.272777 · max 0.516964 · median 0.291293, worst excess (= max − 1) -0.483036 (기록자 산술).

(d) **D1 `_best` 파일 게이트**: §5 D1 형제 행 — "그 GA~GD 는 재지 않았다 (`run_samplecx.py` 는 last 파일만 잰다)" (`reg:306`). 이 기록에서 계산하지 않음.

(e) **F3 가드 발동률·V0·V4·V4b (C2 A)**:
- B64e4: 가드 `C2       -3 M-ours-dscore-C-V0          1853   2560   0.724  2.472e+08` (:18); `C2       +0 M-ours-dscore-C-V0          2279   2560   0.890  4.914e+08` (:19); `C2       +3 M-ours-dscore-C-V0          2430   2560   0.949  1.501e+08` (:20); `C2       +6 M-ours-dscore-C-V0          2428   2560   0.948  2.905e+08` (:21); `C2       +9 M-ours-dscore-C-V0          2400   2560   0.938  5.275e+09` (:22); `C2      +12 M-ours-dscore-C-V0          2250   2560   0.879  4.168e+09` (:23); `C2      +15 M-ours-dscore-C-V0          1780   2560   0.695  1.864e+08` (:24); V0: −3 dB 0.788, b\*→V0 pooled 56:6131, POWERED 0/3 · 3/3 (`tab_B64e4:362–367`); V4: −3 dB 0.150, b\*→V4 pooled 392:96, POWERED 3/3 · 0/3 (`tab_B64e4:374–379`); V4b: −3 dB 0.163, b\*→V4b pooled 363:100, POWERED 3/3 · 0/3 (`tab_B64e4:380–385`).
- B128e4: 가드 `C2       -3 M-ours-dscore-C-V0          1770   2560   0.691  5.734e+07` (:18); `C2       +0 M-ours-dscore-C-V0          2300   2560   0.898  2.814e+11` (:19); `C2       +3 M-ours-dscore-C-V0          2355   2560   0.920  1.475e+09` (:20); `C2       +6 M-ours-dscore-C-V0          2464   2560   0.963  1.965e+15` (:21); `C2       +9 M-ours-dscore-C-V0          2398   2560   0.937  3.456e+09` (:22); `C2      +12 M-ours-dscore-C-V0          2277   2560   0.889  4.577e+09` (:23); `C2      +15 M-ours-dscore-C-V0          1933   2560   0.755  9.339e+08` (:24); V0: −3 dB 0.759, b\*→V0 pooled 57:5944, POWERED 0/3 · 3/3 (`tab_B128e4:362–367`); V4: −3 dB 0.151, b\*→V4 pooled 382:107, POWERED 3/3 · 0/3 (`tab_B128e4:374–379`); V4b: −3 dB 0.157, b\*→V4b pooled 370:107, POWERED 3/3 · 0/3 (`tab_B128e4:380–385`).

(f) **대조군 `b* → b*-scalar`**: §6.1.1 끝.

(g) **best 대 last V1 짝 부호검정 (B32e4 §6.2 형식; a = best 실패·last 성공; 기록자 산술 — raw 의 `M-ours-dscore-C-V1|blk_err[:, -1]`, `analysis.paired` 와 같은 셈)**:
- B64e4 (`raw_B64e4` vs `raw_B64e4last`, 공유 청크 448/448): −3 dB 21:26 (p=0.56), +0 dB 17:6 (p=0.035), +3 dB 5:5 (p=1), +6 dB 1:2 (p=1), +9 dB 0:2 (p=0.5), +12 dB 1:1 (p=1), +15 dB 0:0 (p=1); 판정점 −3/+0/+3 합 43:37 (p=0.58).
- B128e4 (`raw_B128e4` vs `raw_B128e4last`, 공유 청크 448/448): −3 dB 19:18 (p=1), +0 dB 13:2 (p=0.0074), +3 dB 6:7 (p=1), +6 dB 2:3 (p=1), +9 dB 2:0 (p=0.5), +12 dB 0:1 (p=1), +15 dB 2:0 (p=0.5); 판정점 −3/+0/+3 합 38:27 (p=0.21).
- NR16B64e4 (`raw_NR16B64e4` vs `raw_NR16B64e4last`, 공유 청크 192/448): −3 dB 13:13 (p=1), +0 dB 5:4 (p=1), +3 dB 2:0 (p=0.5); 판정점 −3/+0/+3 합 20:17 (p=0.74).

(h) **셀별 절대 격차 ΣF_V1 − ΣF_g, ΣF_b\* − ΣF_g (−3/0/+3 합, 블록 수, 90 %; Q-K 실행 (a) 파일의 `gaps` 줄)**:
- C2 R1 (새): 363 [90% 330, 395] / 664 [90% 624, 704] (`qk_C2_L95:7`)
- C2 R2 (기준): 359 [90% 328, 392] / 711 [90% 671, 752] (`qk_C2_L95:8`)
- C6 R1 (새): 47 [90% 35, 60] / 213 [90% 189, 237] (`qk_C6_L90:7`)
- C6 R2 (기준): 42 [90% 29, 54] / 237 [90% 213, 263] (`qk_C6_L90:8`)

(i) **`<T>last` (last-EMA, 보고 전용) 의 R [90% paired] 와 무결성 줄 `b* last == A`**:
- B64e4last: R 0.486 [90% 0.448, 0.524] (804 · 474 · 125; `rec_B64e4last:5`)
  - 점별 R(last): −3 0.429 [0.386, 0.473] · +0 0.655 [0.577, 0.729] · +3 0.636 [0.450, 0.818] (`rec_B64e4last:2–4`)
  - 무결성 줄: `M-ours-bstar raw_B64e4last == raw_B64e4 (report-only integrity, not a gate): 0 of 3136 (chunk, key) pairs differ -> OK` (`rec_B64e4last:6`); `L:205` rc=0 (게이트 아님).
- B128e4last: R 0.470 [90% 0.429, 0.509] (789 · 477 · 125; `rec_B128e4last:5`)
  - 점별 R(last): −3 0.431 [0.385, 0.478] · +0 0.595 [0.505, 0.677] · +3 0.541 [0.323, 0.725] (`rec_B128e4last:2–4`)
  - 무결성 줄: `M-ours-bstar raw_B128e4last == raw_B128e4 (report-only integrity, not a gate): 0 of 3136 (chunk, key) pairs differ -> OK` (`rec_B128e4last:6`); `L:214` rc=0 (게이트 아님).
- NR16B64e4last: R 0.793 [90% 0.741, 0.845] (253 · 84 · 40; `rec_NR16B64e4last:5`)
  - 점별 R(last): −3 0.779 [0.711, 0.847] · +0 0.760 [0.643, 0.860] · +3 0.926 [0.793, 1.042] (`rec_NR16B64e4last:2–4`)
  - 무결성 줄: `M-ours-bstar raw_NR16B64e4last == raw_NR16B64e4 (report-only integrity, not a gate): 0 of 1344 (chunk, key) pairs differ -> OK` (`rec_NR16B64e4last:6`); `L:223` rc=0 (게이트 아님).

(j) **kron 8192 (보고 전용; 어떤 등록 b\* 에도 들어가지 않음 — 공개 8)**:
- `K8: B64e4 grid + kron 8192 -> b* kron 8192 -2.4856244669792424; dll(8192-4096) +1.8080` (`prep:36`)
- `DRAFT  K8 8192 -2.4856244669792424 1` (`prep:37`)
- K8 적합 `kron K=8192` ll_val -2.4856244669792424 (r0; 311/270 patience; 재시드 24042; sec 51918; 후보 3; `batched [1.0, 1.0, 1.0]`) (`prep:35`)
- S5: `K8 8192 -2.4856244669792424 1` (`S5:9`)
- `--paired raw_B64e4k8 raw_B64e4`: ΣF_b\*(8192) 816 vs ΣF_b\*(4096) 804 (−3/0/+3 합; V1 480/480, genie 125/125), ΔR +0.009 [90% -0.010, +0.028] [95% -0.014, +0.031], p 0.4340 (`K8:3–5`) — ΔR 은 b\* 만의 차이.
- V1 무결성 (`nscale_K8_V1.txt`, 게이트 아님): `M-ours-dscore-C-V1 raw_B64e4k8 == raw_B64e4 (report-only integrity, not a gate): 0 of 1344 (chunk, key) pairs differ -> OK` (`K8_V1:1`); `L:230` rc=0
- 첫 청크 RSS (§1 비용 행 "첫 청크 RSS 를 §6 전사 때 적는다"): runner 로그의 RSS 줄 0 개 — **[판단 필요: RSS 가 기록되지 않음 (run_nscale.sh·runner 가 RSS 를 찍지 않는다); 편차로 적을지]**.

(k) **E128 (`--pair` b\*@N2 vs V1@1e4; V1 @ 1e4 는 D1 게이트 FAIL = 예산 축 측정 — 공개 12)**: A `raw_B128e4` M-ours-bstar SNR@0.1 -1.12 dB [90% -1.30, -0.92; censored 0.0%] (:4) / B `raw_B1e4` M-ours-dscore-C-V1 SNR@0.1 -2.18 dB [90% -2.34, -2.02; censored 0.0%] (:5); Δ +1.06 dB [90% +0.81, +1.32], p 0.0000, censored 0.0% (`eff128_C2:6`).

(l) **시드 산포 캐비엇**: §0.1 의 SEEDS16e4 줄 (`reg:86`) 그대로 — 시드 분산은 부트스트랩에 없다 (공개 3).

(m) **이 기록에서 계산하지 않은 보고 전용 항목** (`run_nscale.sh` 가 출력하지 않고, 이 생성기는 결과 뒤 새 통계를 만들지 않는다): 기존 예산 (1e4·4e4·1.6e5) 과 새 점 사이의 짝 ΔR (§0.3 형식 — P2·S1·S2·K8 줄만 있음), D1 `_best` 파일의 GA~GD.

#### 6.1.6 §4.1 이관분 (§1 비용 행·§4.1 표가 §6 으로 미룬 값 — §0–§5 는 편집하지 않으므로 여기 적는다)
- 태그 소요 합 (runner `finished in` — 줄 번호는 위 runner 표, 기록자 합산): 407.1 min = 6.79 h (BRB32e4 5.2, BRNR16B16e4 34.5, B64e4 34.0, B128e4 34.2, B64e4chk 5.2, B128e4chk 5.2, B64e4last 33.8, B128e4last 33.8, K2B32e4 2.4, K2B64e4 2.4, K2B128e4 2.4, NR16B64e4 124.7, NR16B64e4chk 20.4, NR16B64e4last 46.3, K2NR16B64e4 11.0, B64e4k8 11.6); §1 비용 행 추정 "합 ≈ 7.5–9.5 h" (`reg:162`). eval 전체 경과는 위 실행 절.
- B64e4k8 첫 청크 RSS: §6.1.5 (j).

#### 6.1.7 대체 규칙 상태 (§1 대체 규칙 행; 판정 근거는 적합·학습·검사 사실뿐 — §5 그대로)
- **F1**: `FALLBACK 0` (`S5:4`); `PT B128e4` = 14 필드 (`S5:6`).
- **F2** (C6 6.4e5 실패): `PT NR16B64e4` 정상 → 미발동.
- **F3** (발산 → §3d): S5 stem 의 `_fb<k>` 없음; `prep` 의 `other attempts of this stem`: B64e4 `other attempts of this stem: none` (`prep:27`); B128e4 `other attempts of this stem: none` (`prep:63`); NR16B64e4 `other attempts of this stem: none` (`prep:96`).
- **F4** (일괄 검사 FAIL): B64e4 `batched check results/nr8b_batched_check_S2_n640000.txt: VERDICT: PASS (criterion in the module docstring)` (`prep:4`); B128e4 `batched check results/nr8b_batched_check_S2_n1280000.txt: VERDICT: PASS (criterion in the module docstring)` (`prep:40`); NR16B64e4 `batched check results/nr16b_batched_check_S2_n640000.txt: VERDICT: PASS (criterion in the module docstring)` (`prep:73`).
- **F5** (kron 8192): `K8 8192 -2.4856244669792424 1` (`S5:9`) — b\* = kron 8192 → 실행.
- **F6** (GB′): B64e4 `GMM b* =` 줄 1 개 (`prep:32`); B128e4 `GMM b* =` 줄 1 개 (`prep:68`); NR16B64e4 `GMM b* =` 줄 1 개 (`prep:98`) (실패해도 보고 항목이 빌 뿐; §6.1.5 (c)).

#### 6.1.8 §3 예측 채점 (적중/빗나감 이분; 범위 밖은 빗나감; F1 이면 1.28e6 몫은 '채점하지 않음 (F1)'; '동결 전 확인' 은 채점 제외)

| # | 예측 (요지, 등록 줄) | 결정하는 수 | 채점 |
|---|---|---|---|
| 1 | 일괄 검사 (`reg:244`) | B64e4 `batched check results/nr8b_batched_check_S2_n640000.txt: VERDICT: PASS (criterion in the module docstring)` (`prep:4`); B128e4 `batched check results/nr8b_batched_check_S2_n1280000.txt: VERDICT: PASS (criterion in the module docstring)` (`prep:40`); NR16B64e4 `batched check results/nr16b_batched_check_S2_n640000.txt: VERDICT: PASS (criterion in the module docstring)` (`prep:73`) | 동결 전 확인 (세 개 모두 PASS, §0.5) — 적중·빗나감 어느 쪽으로도 세지 않음 |
| 2 | GMM (`reg:245`) | B64e4 b\* = kron 4096 (`S5:5`) ✓; full 최고 -9.430325411871934 가 b\* -4.2936152070786635 보다 5.137 nat 낮음 (≥ 3) ✓; Δll(4096−2048) 2.5620 ∈ [+1.5, +3.5] (`prep:20`) ✓; c_K 3.4710521640765846 (r < 1) ✓; K2 2048 (구성 가능) ✓; B128e4 b\* = kron 4096 (`S5:6`) ✓; full 최고 -8.81302556797323 가 b\* -3.1746045830106424 보다 5.638 nat 낮음 (≥ 3) ✓; Δll(4096−2048) 3.0008 ∈ [+1.5, +4.0] (`prep:56`) ✓; c_K 4.606498629712138 (r < 1) ✓; K2 2048 (구성 가능) ✓; NR16B64e4 b\* = kron 4096 (`S5:8`) ✓; full 최고 40.77121185010288 가 b\* 81.9525983268529 보다 41.181 nat 낮음 (≥ 3) ✓; Δll(4096−2048) 6.8201 ∈ [+0.8, +3.0] (`prep:89`) ✗; c_K 2.339833725892784 (r < 1) ✓; K2 2048 (구성 가능) ✓ | **빗나감** |
| 3 | 재시드 (`reg:246`) | B128e4 kron 4096 재시드 36 < 3170 (`prep:56`) ✓; NR16B64e4 kron 4096 재시드 30032 < 85594 (`prep:89`) ✓ | **적중** |
| 4 | kron 8192 (보고 전용) (`reg:247`) | Δll(8192−4096) +1.8080 > 0 (`prep:36`) ✓; Δll ∈ [+0.5, +2.5] ✓; K8 run = 1 (`S5:9`) ✓ | **적중** |
| 5 | 학습 (`reg:248`) | V1 B64e4: `stopped_by=patience, aborted=False`, 다른 시행 없음 (`prep:28`) ✓; V1 B128e4: `stopped_by=patience, aborted=False`, 다른 시행 없음 (`prep:64`) ✓; V1 NR16B64e4: `stopped_by=patience, aborted=False`, 다른 시행 없음 (`prep:97`) ✓; D1 6.4e5: `stopped_by=patience, aborted=False`, last 파일 1 개 (`prep:30`) ✓; D1 1.28e6: `stopped_by=patience, aborted=False`, last 파일 1 개 (`prep:66`) ✓; F1 미발동 (`FALLBACK 0`) ✓ | **적중** |
| 6 | D1 게이트 (last) (`reg:249`) | 6.4e5: PASS, GC 0.09603 ∈ [0.07, 0.11] (`prep:29`) ✓; 1.28e6: PASS, GC 0.08180 ∈ [0.07, 0.11] (`prep:65`) ✓ | **적중** |
| 7 | 재현 (`reg:250`) | bridge BRB32e4 ACCEPT 통과 ✓; bridge BRNR16B16e4 ACCEPT 통과 ✓; B64e4chk ACCEPT 통과 ✓; B64e4 genie 재생 (A 파일의 `replay vs` 실패 줄 0) ✓; B128e4chk ACCEPT 통과 ✓; B128e4 genie 재생 (A 파일의 `replay vs` 실패 줄 0) ✓; NR16B64e4chk ACCEPT 통과 ✓; NR16B64e4 genie 재생 (A 파일의 `replay vs` 실패 줄 0) ✓ | **적중** |
| 8 | P1 (`reg:251`) | B64e4: POWERED=True, second 3/3, 판정점 −3/+0/+3 ✓; B128e4: POWERED=True, second 3/3, 판정점 −3/+0/+3 ✓; NR16B64e4: POWERED=True, second 3/3, 판정점 −3/+0/+3 ✓; S_N C2 성립 ✓; S_N C6 성립 ✓ | **적중** |
| 9 | C2 −3 dB BLER (`reg:252`) | B64e4 V1 370/2560 = 0.1445 ∈ [0.135, 0.155] (`rec_B64e4:2`) ✓; B64e4 b\* 591/2560 = 0.2309 ∈ [0.222, 0.240] (`rec_B64e4:2`) ✓; B128e4 V1 370/2560 = 0.1445 ∈ [0.135, 0.155] (`rec_B128e4:2`) ✓; B128e4 b\* 583/2560 = 0.2277 ∈ [0.212, 0.238] (`rec_B128e4:2`) ✓ | **적중** |
| 10 | R (−3/0/+3 합) (`reg:253`) | B64e4 R 0.477 (정확 0.47717) ∈ [0.46, 0.51] (`rec_B64e4:8`) ✓; B128e4 R 0.453 (정확 0.45331) ∈ [0.44, 0.50] (`rec_B128e4:8`) ✓; NR16B64e4 R 0.779 (정확 0.77934) ∈ [0.76, 0.84] (`rec_NR16B64e4:8`) ✓ | **적중** |
| 11 | P2 (`reg:254`) | ΔR_C2 -0.042 (정확 -0.04176) ∈ [−0.06, +0.01] (`P2_C2:5`) ✓; 라벨 (T−) ✗; ΔR_C6 -0.043 (정확 -0.04344) ∈ [−0.07, +0.02] (`P2_C6:5`) ✓; 라벨 (T0) ✓ | **빗나감** |
| 12 | 2차 단계 (`reg:255`) | S1 "판정하지 못함" ✓; S2 "판정하지 못함" ✓ | **적중** |
| 13 | 데이터 효율 (E) (`reg:256`) | Δ +1.11 dB ∈ [+0.9, +1.5] ✓; 90% 하한 +0.86 > 0 (검열 0.0% ≤ 5) ✓ | **적중** |
| 14 | C6 회수율 대역 (`reg:257`) | R(−3 dB) 0.779 (정확 0.77941) ≥ 0.70 ✓ | **적중** |
| 15 | 대조군 (`reg:258`) | B64e4 `second arm fewer failures at 0/3` (= 0/3) ✓; B128e4 `second arm fewer failures at 0/3` (= 0/3) ✓; C6 `first arm fewer failures at 2/3` (≥ 2/3) ✓ | **적중** |
| 16 | GB′ (`reg:259`) | B64e4 median 0.514538 ∈ [0.45, 0.62], worst -0.120408 < 0 (`prep:31`) ✓; B128e4 median 0.513312 ∈ [0.45, 0.62], worst -0.122010 < 0 (`prep:67`) ✓; NR16B64e4 median 0.2913 ∈ [0.22, 0.40], max 0.5170 < 1 (worst excess = max − 1 < 0) (`prep:98`) ✓ | **적중** |
| 17 | K8 (보고 전용) (`reg:260`) | ΣF_b\*(8192) 816 ≤ ΣF_b\*(4096) 804 ✗; ΔR +0.009 ∈ [−0.03, 0] (`K8:5`) ✗ | **빗나감** |
| 18 | 빗나갈 경로 (`reg:261`) | (a) F1 미발동; (b) C6 시행 1 발산 미발동; (c) D1 게이트 FAIL 미발동; (d) (T−) 발동 (C2); (e) bridge 실패 미발동; (f) Q-K 강제 미발동. 격자·K·SNR·시드를 늘리지 않았다 | 예측 항목 아님 |

합계: 적중 13 (3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16), 빗나감 3 (2, 11, 17), 채점 제외 1 (1; 동결 전 확인·F1), 판단 필요 0 (); 18 은 경로 기록.

#### 6.1.9 공개 1–12 (§2.4 "원고·§6 에 그대로" — 등록 문장을 바꾸지 않고 옮김)
1. **순차 선택**: 새 N′ (6.4e5, 1.28e6) 와 셀 (C2, C6) 은 1e4–3.2e5 (C2), 1e4–1.6e5 (C6) 의 테스트 결과를 본 뒤 정했다. (`reg:226`)
2. **기준 결과는 알려져 있다**: 추세의 한쪽 끝 R(3.2e5) = 0.495, R(1.6e5) = 0.823, 그 c_K (2.02, 1), R\* (0.610, 0.806) 가 기록값이며, 작성자는 C2 의 R 이 예산과 함께 줄어 온 것 (§0.3) 을 보고 예측·문구를 정했다. (`reg:227`)
3. **시드 분산은 부트스트랩에 없다**: CI 는 시행 재표본만 반영한다. C2 1.6e5 의 시드 3 개 R 범위 0.011 (SEEDS16e4) 을 옆에 적는다; 새 점은 attempt 1 하나다. (`reg:228`)
4. **테스트 시행 재사용**: 시행 0..2559 는 이전 모든 예산·A1·P3·SCALE 의 같은 시행이다 (짝 비교의 근거이자 재사용). (`reg:229`)
5. **학습 집합은 독립 추출이다**: 6.4e5·1.28e6 집합은 3.2e5·1.6e5 집합을 앞부분으로 포함하지 않는다 (§0.5 `prefix.log`) — ΔR 에는 "데이터를 더 준 효과" 와 "다른 표본" 이 섞인다 (기존 예산 축과 같다). 중첩을 주장하지 않는다. (`reg:230`)
6. **적합 경로가 다르다**: 기준 C2 3.2e5 의 b\* (kron 4096) 는 희소 경로 (sparse_tol 1e-12, `kron_batched` 0) 이고 그 격자 안에도 정확·일괄이 섞였다 (§0.4); 새 kron 적합은 전부 일괄 정확 경로, full 은 정확 경로다. 동등성은 각 검사 (희소: `b32e4_sparse_check.txt`, 일괄: `nr{8,16}b_batched_check_S2_n<N>.txt`) 로만 보증된다. (`reg:231`)
7. **C6 가중치 비대칭**: 기준 C6 1.6e5 는 §3d 시행 2 (fb2, 클리핑 1.0) 가중치이고 새 6.4e5 는 시행 1 (발산하지 않으면) 이다 — ΔR_C6 에는 레시피 차이가 섞일 수 있다. (`reg:232`)
8. **kron 8192 는 보고 전용**이며 어떤 등록 b\* 에도 들어가지 않는다 (별도 적합 태그 `K8B64e4`, BLER 은 링크 집합 태그 `B64e4k8` 로만). Q-K 의 대신이 아니다. (`reg:233`)
9. **Q-K·Q-OP·(E) 는 비짝이다**: `frontier_ci --paired` 가 그 옵션을 받지 않아 `--recovery`·`--pair` (raw 사이 독립 재표본) 로 계산한다 — 같은 시행이라 CI 가 짝보다 넓고, "강건"·(E) 성립 쪽에 보수적이다. 1차 ΔR 만 짝이다. 한정어는 L⁰ (비짝) 기준이며 1차 라벨과 직접 비교하지 않는다 (§2.2). 비짝 SD 가 짝의 1.4–1.7 배 (§0.3) 라 1차가 경계의 (T±) 이면 L⁰ = (T0) 이 되어 '[한정어 판정 불가]' 가 나오는 것이 예상되는 결과다 (결과 뒤 해석이 아니라 지금 적어 둔다). (`reg:234`)
10. **P2 의 SNR 은 고정**: −3/0/+3 dB = 기준점의 기록된 자동 판정점. 새 점의 자동 판정점이 다르면 P1 은 자동 판정점, P2 는 −3/0/+3 을 쓴다. (`reg:235`)
11. **K 상한 교란**: 상한 4096 대비 N′/K 가 예산과 함께 커진다 (C2 78 → 312, C6 39 → 156). b\* 가 상한에 묶이면 GMM 의 개선이 덜 반영될 수 있고 그 방향은 V1 에 유리하다 → Q-K 와 보고 전용 8192 로만 다룬다. C6B16e4 §6.5 의 tol 정지 캐비엇도 새 적합에서 정지 사유로 기록한다. (`reg:236`)
12. **(E) 의 V1 은 헤드라인 legacy-last 가중치**다 (1.6e5 에 `_best` 가 없다). E128 의 V1 @ 1e4 는 D1 게이트 FAIL 이다. (`reg:237`)

#### 6.1.10 편차·캐비엇 (사실만) · 남은 자리표시
- R CI 두 출처 (C2 새 점): `recovery_ci` 0.453 [0.413, 0.493] (`rec_B128e4:8`) vs `--paired` R1 [0.412, 0.493] (`P2_C2:3`) — 난수 흐름이 달라 셋째 자리가 다를 수 있다 (SCALE16e4 §6.1.4 (a) 와 같은 사정).
- R CI 두 출처 (C6 새 점): `recovery_ci` 0.779 [0.722, 0.836] (`rec_NR16B64e4:8`) vs `--paired` R1 [0.721, 0.836] (`P2_C6:3`) — 난수 흐름이 달라 셋째 자리가 다를 수 있다 (SCALE16e4 §6.1.4 (a) 와 같은 사정).
- **§0–§5 의 미갱신 칸** (편집 금지라 값은 여기 적는다): `reg:295` [K8 병합 대기]; `reg:295` [links 대기]; `reg:295` [§5 커밋 때 채움]; `reg:296` [K8 병합 대기]; `reg:296` [links 대기]; `reg:296` [§5 커밋 때 채움]; `reg:273` §4.1 '대기' 칸 (**GB′ 재실행** (격자 확정 뒤, 학습은 완료 상태로 건너뜀; 로그); `reg:278` §4.1 '예정' 칸 (§6 전사 → Fable 기록 감사 → `docs/EXPERIMENTS.) — **[판단 필요: 각 칸의 지금 값 (예: §5 K8 행 = S5 K8 줄·`prep` K8 줄, links = `NSCALE_LINKS_DONE` 로그, §5 커밋 해시 = 위 커밋 절)]**
- p 값은 서술용; 1차는 Holm 규칙, P1·2차는 보정 없음 (§1·§2.4).
- 다음 단계 (§4.1): Fable 기록 감사 → `docs/EXPERIMENTS.md` 행.

<!-- s6_gen.py 표시 집계 (중복 제거): 판단 필요 4 — 기록 전에 모두 해소할 것 -->
