# REVIEW_AUDIT — T2 diffusion CLI 핸드오프 검토사항 재확인

- 작성: 2026-09-23 KST, Claude Code (Opus 5.5)
- 확인 대상 commit: **HEAD `4ad41df9`** (핸드오프 기준 `6ed0613` 이후 11파일 변경 — score.py 는 sigma_tag 배선만, runner.py 는 290행 가드만 변경. 두 변경 모두 아래 판정에 반영)
- 핸드오프: `T2_DIFFUSION_CLI_HANDOFF_KO.md` (업로드). **핸드오프 설명 자체를 근거로 쓰지 않았다.** 각 항목의 근거는 HEAD의 코드 행, 결과·raw 파일, 또는 CPU 점검이다.
- 방법: 5개 클러스터 × (검증 agent 1 + 반박 agent 1). 검증 agent가 상태를 매기고, 독립 반박 agent가 인용 위치를 다시 열고 수치를 재계산해 뒤집기를 시도. **반박 agent가 뒤집은 판정 0건.** 반박 agent가 추가 발견한 항목은 `M*` id로 포함 (같은 증거 기준, 단 2차 반박은 거치지 않음).
- 읽기 전용: 코드·결과 수정 없음, GPU 미사용. CPU 점검(ckpt 키/해시 읽기, κ 계산, raw 재집계, 소표본 Jacobian 진단)만 수행.
- **소표본 수치 주의**: P1-3a 등변 오차, P1-4a r_P, 실경로 비용비(~1.1–1.4x)는 agent가 n=16 수준으로 임시 측정한 값이고 저장소에 저장되지 않았다. P1 진단의 **방향 근거로만** 쓰고 결과로 인용하지 않는다.

상태 어휘: CONFIRMED(주장이 HEAD에서 성립) · ALREADY_FIXED · NOT_REPRODUCED · HYPOTHESIS_ONLY · NOT_CHECKED.  
분류: **FIX** 코드 수정 필요 · **REC** 기록(문서) 정정 · **DIAG** P1 진단/개선 입력 · **OK** 문제 아님(확인만).

> 주의: CONFIRMED는 '주장이 맞다'는 뜻이다. P0-3·S7-d·R-4.1·R-5.1처럼 주장이 '문제 없음'인 항목은 CONFIRMED이면서 분류가 OK다.

## 요약표

| id | 상태 | 분류 | 판정 |
|---|---|---|---|
| P0-1a | CONFIRMED | FIX | train()은 best를 스칼라로만 추적, 매 epoch 현재 model/EMA로 덮어씀. 모든 trainer가 이 경로. 원자적 저장 없음, stopped 플래그 없어 완료된 wrapper 재실행 시 평가된 ckpt가 1 epoch 더 학습되며 변형됨 |
| P0-1b | CONFIRMED | FIX | 헤드라인 V0/V1/V4 전부 d2sx_N160000_a1.pt = last-EMA@1784 (best@1764, 11,260 EMA 업데이트 차이). BEST_WEIGHTS_UNAVAILABLE. NR16(1688 vs 1668), V2/V3(발산 후 EMA)도 동일 |
| P0-1c | NOT_REPRODUCED | OK | EMA shadow는 clone으로 초기화, 현재 aliasing 결함 없음. 단 수정 시 best 스냅샷은 반드시 clone |
| P0-4 | CONFIRMED | FIX | resolve_hp는 argmin attempt가 아니라 마지막 attempt의 hp를 상속. 기록된 ladder에선 상속 필드가 attempt 간 동일해 실영향 없음. Stage C는 이 경로를 안 탐 |
| ckpt/M2 † | CONFIRMED | REC | D1 gate 판정(LADDER GATED, gate_D1_L0.1)도 last-EMA로 측정. min_epochs=200 때문에 best보다 60~167 epoch 뒤 가중치가 gate됨. 판정 뒤집힘 여부는 미확인 |
| S7-a | CONFIRMED | FIX | train_nr16.py가 _init('NR16')/D2_FITS 설정 없이 gmm_selection 호출 → FileNotFoundError, GB' 미산출 |
| ckpt/M1 † | CONFIRMED | FIX | S7-b와 동일 항목(중복 발견) — runner.py:298 가드로 C6에 score arm 미생성 |
| S7-b | CONFIRMED | FIX | runner.py:298 `if Nr != 8` 두 번째 가드가 C6에서 V0/V1/V4 전부 제거. 448/448 raw가 ABSENT (ckpt 클러스터 M1과 동일 항목) |
| s7/M1 † | CONFIRMED | FIX | --stagec-ckpt면 셀 Nr과 무관하게 'Stage C arms ON' 출력, 사전 점검은 파일 존재만 확인 → C6이 arm 없이 완료 |
| S7-c | CONFIRMED | FIX | NR16 ckpt는 사전 등록상 UNGATED(설계). 문제는 run_nr16.sh가 train 실패 여부를 확인하지 않고 BLER로 진행 |
| S7-d | CONFIRMED | OK | NR16 ckpt는 sigma_tag='NR16'을 저장하고 ScorePrior·gb_prime이 읽음. Nr=8 ckpt는 frozen 격자 그대로 |
| G-1.2 | CONFIRMED | REC | D1 PASS를 D2 참-score 검증이라 쓴 곳은 없음. 다만 PAPER_MATERIALS:819 자체 규칙을 어기고 D2 ckpt를 '게이트 통과'라 부른 문구가 STATUS 9곳·PAPER_MATERIALS 2곳 |
| P0-2a | CONFIRMED | FIX | bench_moduleH는 GMM을 denoise_full로 측정하지만 M-ours-bstar는 매 반복 ep_site(G,b,lam_min) 호출 → 잘못된 함수를 측정 |
| P0-2b | CONFIRMED | REC | complexity_moduleH.txt는 K=512·N=1e4 ckpt. 4.6x가 STATUS/NUMBERS_PACKAGE/F14에서 arm 간 비용비로 인용됨 |
| cost/M2 † | CONFIRMED | REC | 같은 코드로 재측정 시 4.6x가 아니라 6.2~6.3x(부하 민감, 평균만 기록). 실경로(ep_site vs V1) K=1024 비율은 임시 측정 ~1.1~1.4x — 저장 안 된 비통제 측정 |
| F14-cost | CONFIRMED | FIX | K=1024 inference 비용 측정은 저장소 어디에도 없음 (P0-2a 새 벤치로 해결) |
| cost/M1 † | CONFIRMED | REC | F14b 캡션이 K=1024라 쓰지만 실제 raw_B1e4lo는 K=512. figure_f14.py가 캐비엇을 하드코딩, F14c는 stale |
| cost/M3 † | CONFIRMED | REC | tables_D2_B16e4k.txt에 K=1024가 한 번도 안 나오고 내장된 옛 gate 표의 K=512만 나옴 (analysis.py가 kron_K 미출력) |
| P0-3 | CONFIRMED | OK | T_IN=5는 R3 BiG-AMP 전용, n_inner=1은 RouteA. T_IN 변경은 제안 수신기에 영향 없음 |
| P1-3a | CONFIRMED | DIAG | DiT는 전역 위상 등변성을 구조적으로 강제하지 않음. 예비 측정(n 소수, 미저장) 등변 오차 중앙값 8.3e-3/2.25e-2/4.5e-2 @σ=0.033/0.182/0.845 = denoising 오차의 29/16/7%. GMM 대조군 ~1e-15 |
| P1-3b | CONFIRMED | DIAG | 학습 루프·D2 데이터에 전역 위상 augmentation 없음 |
| P1-4a | CONFIRMED | DIAG | Module H는 nu·J만 쓰고 K(pseudo)는 어디서도 형성 안 함. 인자 규약은 toy로 1e-15 정확. 예비 r_P(n=16) 학습망 0.30/0.47/0.51, 정확 GMM(K=1024) 0.002/0.127/0.306 → 저σ의 망 K는 대부분 가짜, 고σ엔 실제 pseudo-cov 존재 |
| denoiser/M1 † | CONFIRMED | DIAG | GMM Module H도 mixture pseudo-cov를 버림 → widely-linear 확장을 score arm에만 넣으면 adapter 이득과 prior 이득이 섞임 |
| P1-4b | CONFIRMED | DIAG | V1 project_psd는 무차원 J에 floor 1e-6(lmax 무제한). EP site precision clip(clip='eta')은 별개 후속 단계 |
| denoiser/M2 † | CONFIRMED | DIAG | 저장소 n=128 기록: frac lmin(Herm J)<0 = 0.81/0.92/0.078, sym J_R 비PSD 0.99/1.00/0.30 → σ≲0.2에서 대부분 query가 indefinite |
| P2-Ca | CONFIRMED | DIAG | clip='mean'은 존재(t2_gmm.py:65,121). 최신 동일예산 V1/GMM에서 mean vs eta 대칭 비교는 없음 (N=1e4 V0 진단만) |
| denoiser/M3 † | CONFIRMED | DIAG | clip='mean'은 score arm(등방 cavity belief 평균)과 GMM arm(최종 colored belief 평균)에서 보존하는 양이 달라 대칭 ablation이 아님 |
| P2-Cb | CONFIRMED | DIAG | V2 발산·GC FAIL(lr 교란 명시), V3 λ=1 GB/GC/GD FAIL. 실패 원인을 PSD로 기록한 적 없음, V2 PSD 측정 없음 |
| P1-1 | CONFIRMED | DIAG | 궤적 훅 일부 존재(diag_ep_site 등) 하지만 V1 arm·B16e4k fits·q/G/b/J 덤프 없음. production raw엔 nu_q/alphaH 미저장 |
| denoiser/M4 † | CONFIRMED | DIAG | diag_scale·jacobian_psd·review_V1_receiver도 훅 보유. ScorePrior.query_stats(격자 이탈 비율)는 계산되지만 raw에 저장 안 됨 |
| R-4.1 | CONFIRMED | OK | 핸드오프 §4.1 수치 전부 raw에서 재현 (623/371/87/1517/394/839, NMSE 중앙값, kron K=1024, N=1.6e5) |
| R-5.1 | CONFIRMED | OK | κ(L) 1.614392~1.745942, marginal 1.703212 재현. MC 1.70264. d2.py 전력 프로파일 일치(인덱스 시작점 무관) |
| R-5.2 | CONFIRMED | REC | d2.py:19-21, 05_SPEC:23이 '3GPP 계열 = α~CN → GMM correctly specified'로 요약. Sionna/38.901은 명시 안 됨 |
| results/M-5.2a † | CONFIRMED | REC | 01_RULES:77·d2.py·PAPER_MATERIALS는 D2를 '물리적으로 표준'이라 하고 NUMBERS_PACKAGE:695는 그 주장을 철회 — 기록 내부 모순. 01_RULES는 사용자 소유라 제안만 |
| R-10.1 | CONFIRMED | REC | '꼬리 87% 겹침 → score 개선 배제' 문구 STATUS:1719-1721, DECISIONS:104, 커밋 6ed06139에 존재. 같은 데이터에서 V1이 GMM 꼬리의 69%(563/813)를 제거 → 과해석 |
| results/M-10.1a † | CONFIRMED | REC | STATUS:1704-1705의 첫 패스 NMSE 임계값은 사실 분위수 구간(하위 25%/상위 10%). '첫 패스 prior 무관'은 표본공분산 Gaussian LMMSE |
| R-10.2 | CONFIRMED | REC | '나쁜 고정점, 반복은 레버 아님' 문구 존재. 수치(중앙값 0.1853→0.1938)는 재현되나 residual/cycle 진단 없음. 꼬리 289개 중 4스텝 변화<1e-3은 26.3%뿐 |
| R-10.3 | CONFIRMED | REC | 'genie 실패는 prior로 못 줄임', 표 헤더 'Upper bound = genie only'. raw: genie 87, V1∩genie 72, V1 성공·genie 실패 15 |
| results/M-10.3a † | CONFIRMED | REC | 05_SPEC:48, 00_GOAL:111, F11 캡션, R6-exactEP도 '상한'으로 명명 — 반복 EP 수신기이지 bound 아님 |

† 반박 agent가 추가 발견한 항목.

## 핵심 판정

1. **P0-1 확정, 과거 결과는 복구 불가.** 헤드라인 diffusion arm(V0/V1/V4, B16e4k)이 평가한 가중치는 `d2sx_N160000_a1.pt`의 last-EMA(epoch 1784, ema sha256[:16] `a43f1105eb27a29b`, file `4443921ce8d5c4a1`)이고, 보고된 val loss는 best epoch 1764의 값(3.519379e-01)이다. 평가 가중치 자체의 val은 3.519602e-01 (상대차 6.3e-5). best EMA는 어디에도 저장되지 않았다 → **`BEST_WEIGHTS_UNAVAILABLE`**. 과거 표는 덮어쓰지 않고 이 사실만 manifest에 기록한다.
2. **§7 C6(Nr=16) 실행은 diffusion arm 없이 끝났다.** 원인은 runner.py:298의 두 번째 가드와, 이를 잡지 못한 사전 점검. GB' 산출 실패는 train_nr16.py의 D2_FITS 미설정. **train_nr16.py를 그대로 재실행하면 resume=True 때문에 평가된 ckpt가 변형된다**(P0-1a 부수 위험).
3. **복잡도 4.6x는 헤드라인 수신기 비용비가 아니다.** 잘못된 GMM 함수(denoise_full), K=512, N=1e4 ckpt, 부하 민감(재측정 6.2x). 실경로 K=1024 측정은 없다.
4. **§10 과해석 문구는 기록에 실제로 있다** (STATUS, DECISIONS, 커밋 6ed06139, 표 헤더). 원문은 보존하고 날짜 붙은 정정 항목을 추가하는 방식으로 처리할 대상.
5. **P1 진단 대상은 실재한다.** 위상 등변성 미강제·augmentation 없음, pseudo-cov(K)는 score·GMM 양쪽에서 버려짐, V1의 J는 σ≲0.2에서 대부분 indefinite, clip='mean' 대칭 비교 없음. 단 효과 크기는 아직 모른다.

---

## 항목별 근거 (검증 agent 원문 + 반박 agent 재확인)

### ckpt/P0-1a — CONFIRMED · FIX

**주장**: score.train() tracks best_val/best_epoch only as scalars and saves the current model.state_dict() and current ema.shadow every epoch, and no training wrapper keeps separate best weights.

**위치**: `conf/code/score.py:673-684`, `conf/code/score.py:799`, `conf/code/score.py:865-884`, `conf/code/score.py:910-914`, `conf/code/run_d2_sx.py:29-35`, `conf/code/train_nr16.py:36-44`, `conf/code/run_V3.py:47-48`, `conf/code/run_V3.py:68-70`, `conf/code/run_d2_V2.py:44-46`, `conf/code/run_d2_V2.py:61-63`, `conf/code/hpo.py:117-123`, `conf/code/hpo.py:286-291`, `conf/code/runner.py:612-626`, `conf/code/run_B3.py:16-20`, `conf/code/run_samplecx.py:16-19`, `conf/code/run_d1_variant.py:59`

**방법**: Read train() at HEAD and git diff 6ed0613..HEAD -- score.py (the only change is sigma_tag plumbing; the best/save logic is the same). grep for torch.save, best_val, deepcopy and shadow across conf/code/*.py. Read every score.train caller. Also checked the checkpoint key sets on CPU.

**근거**: Best tracking is scalar only: L799 `ep0, best, best_ep, hist = 0, np.inf, -1, []` and L867-869 `imp = vl < best - 1e-12; if imp: best, best_ep = vl, ep`. Nothing is copied when val improves. The save at L875 runs every epoch whether or not val improved: `torch.save(dict(epoch=ep, model=model.state_dict(), ema=ema.shadow, ..., best_val=best, best_epoch=best_ep, ...), cpath)`. The return at L910 is `val_loss=best`, so any caller that logs res['val_loss'] reports the best-epoch loss (d2_gbprime.csv via run_d2_sx.py L51, LADDER rows via ladder_append), while the file holds last-epoch weights. `grep torch.save conf/code/*.py` matches only score.py. Every production trainer goes through score.train(ckpt=...) with no extra save: run_d2_sx, train_nr16, run_V3, run_d2_V2, hpo (search+final), runner cmd_train, run_B3, run_samplecx, run_d1_variant. The other Adam loops (arch_uvit/adm/dit/energy, param_edm, selftest_V2) are all inside _selftest functions. None of the 7 checkpoints I opened has a best-weights key; keys are {Nr,Nt,attempt,best_epoch,best_val,device,ema,epoch,hp,model,opt,prior,rng,rung,split_hash,testbed,wall_sec[,jac_reg,rng_jac,grad_clip,sigma_tag]}. Related hazard: the checkpoint stores no stopped_by/done flag, and every wrapper uses resume=True. Re-running a finished wrapper therefore loads epoch E and trains epoch E+1 (L839 `for ep in range(ep0 + 1, ...)`). The patience stop only happens after that epoch, and the file is overwritten first. So re-running run_d2_sx.py --ntrain 160000 --attempt 1, or train_nr16.py, would silently mutate an evaluated checkpoint. The main save is also a plain torch.save to cpath, with no tmp file or atomic replace.

**수정 방향(제안)**: Opt-in and additive, inside score.train only (Demo/ untouched). When `imp`, snapshot `best_ema = {k: v.detach().clone() for k, v in ema.shadow.items()}` and write a sibling `<cpath>_best.pt` (ema=best_ema, epoch=best_ep, best_val=best, hp, rung, Nr, Nt, sigma_tag, split_hash) via torch.save(tmp) + os.replace. Keep cpath as the resume/last file (optionally make its save atomic too; the content stays the same). Record stopped_by in the checkpoint and have train() return right away when a resumed checkpoint is already stopped, so a re-run cannot mutate an evaluated file. Evaluation keeps reading whatever path the caller passes, so existing behaviour is the default; new runs go under a new tag.

**반박 검토** (agree=True, → CONFIRMED): Re-read score.py at HEAD. L799 `ep0, best, best_ep, hist = 0, np.inf, -1, []`. L867-869 track best as a scalar only. L875-884 torch.save(dict(epoch=ep, model=model.state_dict(), ema=ema.shadow, ...), cpath) runs every epoch. L910 returns val_loss=best. git diff 6ed0613..HEAD -- score.py only adds sigma_tag. `grep torch.save` over the whole repo (Demo excluded) matches only score.py:875. Every production caller routes through score.train: run_d2_sx.py:33, train_nr16.py:42, run_V3.py:68, run_d2_V2.py:61, hpo.py:121/289, runner.py:626, run_B3.py:19, run_samplecx.py:19, run_d1_variant.py:59. The remaining Adam loops (arch_energy/uvit/adm/dit, param_edm, selftest_V2) all sit inside selftests. None of the 13 d2sx checkpoints has a best-weights key. The mismatch shows up in a result file: results/d2_gbprime.csv row `160000,1,...,1784,3.519379e-01` pairs the last epoch (1784) with the best-epoch val. The re-run mutation hazard holds: the save at L875 comes before the divergence and patience checks at L892-897, so resuming the finished N160000_a1 trains epoch 1785 and overwrites the file before it stops (1785-1764=21>=20). Nuance the verifier missed: resuming a DIVERGED checkpoint is worse. L837 resets ndiv=0, and patience cannot fire below min_epochs=200 (V2 a1 ep 118, V3 a1 ep 62), so a re-run would overwrite for at least 5 more epochs before the divergence guard fires again. hpo passes resume=False to fresh paths, so it carries no mutation risk. runner cmd_train (L626) uses the default resume=True.

### ckpt/P0-1b — CONFIRMED · FIX

**주장**: load_model() loads st['ema'], which is the last-epoch EMA. The headline Stage C arms V0, V1 (psd_project) and V4 in tables_D2_B16e4k / raw_B16e4k all load conf/ckpt/d2sx_N160000_a1.pt, whose stored EMA is from epoch 1784 while the best validation epoch is 1764.

**위치**: `conf/code/score.py:918-922`, `conf/code/score.py:950`, `conf/code/score.py:1037-1082`, `conf/code/runner.py:297-303`, `conf/code/runner.py:316-318`, `conf/code/runner.py:323-324`, `conf/results/tables_D2_B16e4k.txt:37-45`, `conf/logs/train_d2sx_N160000_a1.log:1771`, `conf/logs/train_d2sx_N160000_a1.log:1790-1792`, `conf/code/queue2.sh:23`

**방법**: Traced the call path: runner --stagec-ckpt → score_prior → score.load_prior(ckpt=explicit) → ScorePrior → load_model. Scanned 'meta|stagec_ckpt' in all 448 raw_B16e4k/*.npz. On CPU I torch.load-ed the checkpoint and read epoch, best_epoch, best_val and hist, and hashed the ema and model tensors with sha256 (sorted keys + raw bytes, first 16 hex). Read the training log. Did the EMA-decay arithmetic.

**근거**: L922: `m.load_state_dict({k: st["ema"][k]...})`. The checkpoint holds only one EMA, the one saved at the last epoch. runner L301-302 builds V0/V4 (spc) and V1 (spc1, psd_project=True) from the same stagec_ckpt. All 448 raw_B16e4k files have meta|stagec_ckpt = /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt, matching tables header L37-39 and L44. d2sx_N160000_a1.pt: epoch=1784, best_epoch=1764, best_val=3.519379e-01, hist val at 1784 = 3.519602e-01 (relative gap 6.3e-5). ema sha256[:16]=a43f1105eb27a29b, model sha256[:16]=985cc41fbb69820a, file sha256[:16]=4443921ce8d5c4a1, mtime 2026-09-21 22:37, before the raw files (2026-09-22 21:23-21:26). The log agrees: L1771 `epoch 1764 | ... val 3.519379e-01 ... *`, L1791 `epoch 1784 | ... val 3.519602e-01`, L1792 `# done: 1784 epochs, stopped_by=patience ... best val 3.519379e-01 @ epoch 1764`. It is one session with no resume. n_train=144000 at batch 256 gives 563 EMA updates per epoch, so 20 epochs is about 11,260 updates, and 0.999^11260 ≈ 1.3e-5. The evaluated EMA is effectively a different weight set from the best-epoch EMA, even though its val loss is almost the same. Code reading shows val_loss() (L865) is computed from exactly the shadow saved at L875, so the evaluated weights' own val loss is the recorded 3.519602e-01, not the reported 3.519379e-01. BEST_WEIGHTS_UNAVAILABLE: the best-epoch (1764) EMA is stored nowhere, so it cannot be recovered after the fact. The raw meta records only the path; there is no checkpoint hash or epoch. The same pattern holds for siblings: a2 1378 vs 1358, a3 1044 vs 1024, N10000_a1 673 vs 653, NR16_N10000_a1 1688 vs 1668 (ema d78ac54571f89344; there 0.999^720 ≈ 0.49). For the diverged V2 a1 (118 vs 85, last val 1.2075 vs best 0.3654) and V3 a1 (62 vs 27, last 1.720 vs best 0.692), the stored EMA is the post-divergence one.

**수정 방향(제안)**: Do not rewrite past results. Mark the B16e4k Stage C arms (V0/V1/V4) and NR16run as BEST_WEIGHTS_UNAVAILABLE, evaluated = last-EMA @1784 (ema a43f1105eb27a29b, file 4443921ce8d5c4a1), reported val = best @1764, in the manifest. Additive: have runner.build_point write meta['stagec_ckpt_sha256'], meta['stagec_ckpt_epoch'] and meta['stagec_ckpt_best_epoch'] (new keys, existing keys untouched). A best-weights re-evaluation needs a retrain under a new tag once P0-1a is fixed.

**반박 검토** (agree=True, → CONFIRMED): Re-ran the CPU check. d2sx_N160000_a1.pt: epoch 1784, best_epoch 1764, best_val 3.519379e-01, last hist val 3.519602e-01. Hashes: ema a43f1105eb27a29b, model 985cc41fbb69820a, file 4443921ce8d5c4a1. mtime 09-21 22:37, before raw_B16e4k (09-22 21:23-21:39). Log: L4 n_train=144000, L1771 epoch 1764 *, L1790-1792 done at 1784; one session only. EMA arithmetic: ceil(144000/256)*20 = 11260 updates, 0.999^11260 = 1.28e-5. All 448 raw_B16e4k files have meta|stagec_ckpt=d2sx_N160000_a1.pt. The only other ckpt-related key is meta|ntrain (no hash, no epoch). Corrections: (1) M-ours-dscore-C-V4b also uses score_prior_c (arms.py:175-182), so it is also last-EMA. The list 'V0, V1, V4' is incomplete. (2) queue2.sh:23 is the B16e4 run (tag B16e4), not B16e4k. B16e4k was launched by refit_gmm_extended.sh:22-23 with $CKPT (logs/run_D2_B16e4k.log names the same ckpt), so the conclusion is unchanged. (3) The fix sketch's 'mark NR16run as BEST_WEIGHTS_UNAVAILABLE' is wrong: raw_NR16run never loaded any score checkpoint (runner.py:298 `if Nr != 8`, see missed M1). (4) The scope is wider than B16e4k. Every Stage C raw dir evaluates a last-EMA file: raw_B16e4 (1344 files, same ckpt); raw_B1e4/B1e4lo/B1e4x (d2sx_N10000_a1, 673 vs best 653); raw_B1e4s2 (a2, 657 vs 637); raw_B1e4s3 (a3, 662 vs 642); raw_B4e4/B4e4k/B4e4k1 (d2sx_N40000_a1, 1051 vs 1031); raw_C (d2sx_N160000_a1, plus sx_N160000_D1.pt at ep 200 vs best 136); raw_supp (dscore_ckpt d2sx_N10000_a1). Every ckpt mtime precedes its raw files; e.g. the first raw_C D2 file is 09-21 23:05, after the 22:37 ckpt. So no evaluation read a checkpoint mid-training.

### ckpt/P0-1c — NOT_REPRODUCED · OK

**주장**: The EMA shadow is held by reference (a dict of live tensors), so storing it without a clone would alias.

**위치**: `conf/code/score.py:673-684`, `conf/code/score.py:802`, `conf/code/score.py:875`

**방법**: Read _EMA and every use of `shadow`/`["ema"]` (grep across conf/code/*.py).

**근거**: No aliasing defect exists at HEAD. L676 initialises with `{k: v.detach().clone().float() ...}`, a real copy. L681 updates the shadow tensors in place (`s.mul_(...).add_(...)` / `s.copy_(v)`). L875 hands the live dict to torch.save, which serialises synchronously, so the file cannot change afterwards. The resume path L802 `ema.shadow = {k: v.to(dev) ...}` does not copy when st was already loaded with map_location=dev (L767), so the shadow aliases st['ema']. But st is never read after L806, so this is harmless. No best-EMA dict is kept anywhere, so there is nothing to alias. Latent hazard for the P0-1a fix: because update() mutates in place, a naive `best_ema = ema.shadow` or `dict(ema.shadow)` WOULD alias, so the fix must use detach().clone(). selftest_V3.py L162 only compares loaded checkpoints.

**반박 검토** (agree=True, → NOT_REPRODUCED): L676 is a real copy (`v.detach().clone().float()`), and L681 updates in place. L802 aliases st['ema'] when map_location=dev. An awk scan of L806-915 shows `st` is never referenced after the resume block, so this is harmless. The only other readers of shadow/["ema"] are score.py:922 (load) and selftest_V3.py:162 (compare). I also checked a second latent path. _EMA casts every tensor to float, so the non-float `s.copy_(v)` branch is dead, and integer buffers would be EMA-averaged. A CPU scan of all checkpoints found no non-float model tensors, so this cannot corrupt anything at HEAD. The verifier's warning holds: a P0-1a fix must clone and must not keep dict(ema.shadow).

### ckpt/P0-4 — CONFIRMED · FIX

**주장**: resolve_hp() takes the minimum gate score per rung but then reads hp from the last existing attempt of the winning rung, not from the argmin attempt. Stage C, which passes hp explicitly, never reaches this path.

**위치**: `conf/code/score.py:691-729`, `conf/code/score.py:700-706`, `conf/code/score.py:767-774`, `conf/code/runner.py:626`

**방법**: Read resolve_hp and train()'s hp dispatch. Read every Stage C wrapper's score.train call. On CPU, read the hp of the L1-L5 D1 checkpoints and the base-selection lines in logs/train_L[345]_a*_D1.log.

**근거**: L709-716: `for r in cand: for a in range(1, MAX_ATTEMPTS+1): ... sc[r] = min(sc.get(r, np.inf), gate_score(g))`. The argmin attempt is never recorded. L720 `base = min(ok, key=ok.get)` picks the rung. L722-724: `for a in range(1, MAX_ATTEMPTS + 1): if os.path.exists(ckpt_path(base, a, testbed)): bhp = torch.load(...)["hp"]` has no break, so bhp comes from the LAST existing attempt (a3 when all 3 exist, MAX_ATTEMPTS=3 at L143). L726-728 then copy param/domain/arch from bhp. The non-D1 branch L700-705 returns the FIRST existing D1 attempt (a1), regardless of gate score. Practical impact on the recorded ladder is nil: across attempts 1-3 the inherited fields are identical in every candidate rung (L1 mlp/ve/pixel, L2 mlp/vp/pixel, L3 mlp/vp/angle, L4 conv/vp/pixel; attempt overrides touch only lr/ema/width/depth). Logged selections: L3 and L4 base=L2 (scores L1 4.625, L2 4.511, L3 4.793), L5 base=L4 (L4 2.109). Stage C does not route here: train() L768-769 `if hp is not None: sel = {}`, and run_d2_sx L33, train_nr16 L42, run_V3 L68, run_d2_V2 L61 and run_d1_variant L59 all pass hp=HP. Only the ladder path runner.cmd_train (L626, no hp) and a fresh train() with hp=None reach resolve_hp.

**수정 방향(제안)**: In resolve_hp, keep `best = (score, rung, attempt, path)` inside the loop, load bhp from that exact path, and return it in sel as {rung, attempt, ckpt, score, hp}. Add a check that the inherited hp equals torch.load(argmin path)['hp'] for the resolved fields. No existing checkpoint or result changes, because the inherited fields are identical across attempts.

**반박 검토** (agree=True, → CONFIRMED): Re-read score.py:700-705: the non-D1 branch returns the FIRST existing D1 attempt, regardless of score. L709-716 take the per-rung min without recording the attempt. L720 picks the base. L722-724 loop over attempts with no break, so bhp comes from the LAST existing attempt (MAX_ATTEMPTS=3 at L143). A CPU dump of the L1-L5 D1 hp confirms that the inherited arch/param/domain are identical across a1-a3 (L1 mlp/ve/pixel, L2 mlp/vp/pixel, L3 mlp/vp/angle, L4 conv/vp/pixel, L5 conv/rf/pixel), so the recorded ladder is unaffected. The logged base-selection lines in train_L[345]_a*_D1.log match the verifier: L3/L4 base=L2 (L1 4.625, L2 4.511, L3 4.793), L5 base=L4 (L4 2.109). Stage C bypasses this path through train() L768 `if hp is not None: sel = {}`. Two nuances the verifier missed. (a) The gate scores behind this selection come from gates_D1 → load_model, which reads the last EMA; L4_a3 is gated at ep 200, while its best is at ep 125 (val 0.7374 vs 0.7288). (b) resolve_hp calls ckpt_path(r, a, testbed) with the default CKPT_DIR (score.py:79), but runner.cmd_train writes to d_ckpt() (runner.py:622). Under --tag, the candidate lookup therefore reads the untagged ckpt/ directory. This is latent: only ckpt/ and ckpt_hpo/ exist.

### ckpt/M2 — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: D1 gate verdicts (LADDER.md GATED rows, gate_D1_L0.1.txt, and the gate scores inside resolve_hp) are measured on the last-epoch EMA. The min_epochs=200 floor forces several rungs to train 60-167 epochs past their best epoch, so the gated weights have much worse val loss than the best val printed in the same LADDER entry.

**위치**: `conf/code/score.py:896-897`, `conf/code/score.py:918-922`, `conf/code/score.py:1083-1087`, `conf/LADDER.md:30-47`, `conf/results/gate_D1_L0.1.txt:10-35`

**방법**: CPU torch.load of every non-d2sx checkpoint for epoch, best_epoch, best_val and last hist val. Matched against the LADDER.md train/gate rows and the gate_D1_*.txt checkpoint lines. The gates path _as_model → load_model reads st['ema'].

**근거**: L5_a3: best 1.0488 @100, gated EMA @200 has val 1.6778. LADDER:37 prints 'val 1.049e+00'; LADDER:39 gate GB +109.16%, GC 8.8627, FAIL. L4u_a3: 0.7321 @70 vs 0.9928 @200 (LADDER:38 GB +51.99%, GC 6.10). L4u_a1: 0.7343 @74 vs 0.8926 (LADDER:41). L6_a3: -0.0616 @107 vs 0.6225 (LADDER:47 GB +119.81%). L5_a1: 1.0439 @117 vs 1.1323. gate_D1_L0.1.txt gated sx_V3_N160000_D1_a2_lam0.1.pt at ep 200, best at ep 33 (0.74589 vs 0.74226). Whether any verdict would flip on best weights cannot be settled by code reading. The smaller-gap rungs (L3, L4 a1/a2) also FAIL, so that part is HYPOTHESIS_ONLY. The mismatch itself is established.

**수정 방향(제안)**: Covered by the P0-1a fix: once <ckpt>_best.pt exists, have gates_D1/load_model read it only when the caller opts in (new flag or new path), and record which file was gated in the gate txt/LADDER row. Mark existing gate rows as evaluated on last-EMA and do not rewrite them. A best-weights gate re-run needs retraining under a new tag.

### ckpt/S7-a — CONFIRMED · FIX

**주장**: conf/code/train_nr16.py never calls runner._init('NR16') (or sets arms.D2_FITS), so its post-training GB' step looks for the Nr=16 GMM fits in the untagged directory and crashes.

**위치**: `conf/code/train_nr16.py:30-61`, `conf/code/runner.py:95-113`, `conf/code/arms.py:56-67`, `conf/code/fit_gpu.py:83`, `conf/code/fit_nr16.sh:8-10`, `conf/code/run_nr16.sh:24-30`, `conf/logs/train_nr16.log`

**방법**: Read train_nr16.py, runner._init/d_fits_d2, arms.fit_path/load_fits/gmm_selection, fit_gpu.py, fit_nr16.sh and run_nr16.sh. Listed both fit directories. Read logs/train_nr16.log and logs/queue.log.

**근거**: _init is defined in runner.py (L105-113), not common.py; common.py has none. It sets `A.D2_FITS = d_fits_d2()` = results/gmm_fits_D2_<TAG>. fit_gpu.py L83 calls `_init(tag)`, so fit_nr16.sh (TAG=NR16) wrote the 12 fits to results/gmm_fits_D2_NR16/. arms.py L56 defaults D2_FITS to results/gmm_fits_D2, which has 24 files and no Nr16 ones. train_nr16.py imports arms, never calls _init or sets D2_FITS, and calls `A.gmm_selection("D2", PRIOR, NR, a.ntrain)` at L49. logs/train_nr16.log: `[nr16] trained 1688 ep, val 2.33129e-01 ... stopped_by=patience`, then a traceback at train_nr16.py line 49 → arms.py line 79: `FileNotFoundError: no GMM fits for D2/S2/Nr=16`. No results/d2_gbprime_NR16_*.npz exists, so the NR16 GB' report was never produced. The checkpoint was already saved (epoch 1688), and run_nr16.sh continued to step 4, where runner main calls _init('NR16run') (L1043) via the gmm_fits_D2_NR16run symlink. The C6 BLER run itself is therefore unaffected; only GB' is missing.

**수정 방향(제안)**: In train_nr16.py main(), before gmm_selection, call `A.D2_FITS = os.path.join(C.CONF, 'results', 'gmm_fits_D2_NR16')` (or `from runner import _init; _init('NR16')`). Do NOT recover GB' by re-running train_nr16.py as is: resume=True would train epoch 1689 and overwrite d2sx_NR16_N10000_a1.pt, which raw_NR16run evaluated (see P0-1a). Run GB' through a separate eval-only path (gb_prime on the existing checkpoint with sigma_tag='NR16'), or guard training behind a stopped flag first.

**반박 검토** (agree=True, → CONFIRMED): The claim holds. train_nr16.py:30-61 never sets A.D2_FITS or calls runner._init. The default is arms.py:56 results/gmm_fits_D2 (24 files, none for Nr=16). fit_gpu.py:83 `_init(tag)` routed the 12 Nr=16 fits to results/gmm_fits_D2_NR16/ (confirmed by listing). logs/train_nr16.log: 'trained 1688 ep, val 2.33129e-01 ... stopped_by=patience', then FileNotFoundError at train_nr16.py:49 → arms.py:91 (gmm_selection) → arms.py:79. No results/d2_gbprime_NR16_* exists. I disagree with two statements in the evidence and fix sketch. First, 'The C6 BLER run itself is therefore unaffected; only GB' is missing' is false. runner.py:297-302 still has `if Nr != 8: sc_why = "ABSENT -- M-ours-dscore-C-* only: " + NO_SCORE`; commit 4ad41df9 widened only the M-ours-dscore guard at L290. All 448 raw_NR16run files carry stagec_status 'ABSENT -- M-ours-dscore-C-* only: n/a (no score model for this array size)' and contain no dscore arm, and tables_D2_NR16run.txt:51 lists V0/V1/V4/V4b as absent. C6 therefore produced no diffusion number at all: neither GB' nor BLER. Second, the checkpoint was NOT 'evaluated by raw_NR16run'; the raw meta records its path only. The warning against re-running train_nr16.py as is still stands, because it would overwrite the only Nr=16 model (resume → epoch 1689).

### ckpt/M1 — CONFIRMED · FIX (반박 agent 추가 발견)

**주장**: Because of runner.build_point's `Nr != 8` guard, the §7 C6 (Nr=16) BLER run built no Stage C score arm even though --stagec-ckpt was passed. The NR16 pipeline reported NR16_PIPELINE_DONE with no diffusion arm in it.

**위치**: `conf/code/runner.py:287-302`, `conf/code/run_nr16.sh:26-32`, `conf/results/tables_D2_NR16run.txt:35-51`, `conf/raw_NR16run/`, `conf/logs/queue.log`

**방법**: Read runner.py build_point and git diff 6ed0613..HEAD -- runner.py. Scanned the meta and arm budget keys of all 448 raw_NR16run/*.npz on CPU. Read the tables header and queue.log.

**근거**: runner.py:290 was widened to `if Nr in (8, 16)` for M-ours-dscore, but L297-299 is still `if stagec_ckpt: if Nr != 8: sc_why = "ABSENT -- M-ours-dscore-C-* only: " + NO_SCORE`. Every raw_NR16run file has meta|stagec_status = 'ABSENT -- M-ours-dscore-C-* only: n/a (no score model for this array size)', and the union of arms is {M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32, R0-R5}, with no dscore arm. tables_D2_NR16run.txt:51 lists 'M-ours-dscore-C-V0', 'C-V1', 'C-V4', 'C-V4b' as absent. queue.log shows step 4 running from 04:03 to 04:07, which fits GMM-only arms, followed by 'NR16_PIPELINE_DONE'. The runner's own comment at L1036 warns about exactly this case ('a table with V0/V1/V4 missing'). Its file-exists guard does not catch it, because the file exists.

**수정 방향(제안)**: Change the guard at runner.py:298 to `if Nr not in (8, 16)`, mirroring L290. Better, compare torch.load(stagec_ckpt)['Nr'] with Nr and refuse on a mismatch. Only --stagec-ckpt runs with Nr=16 change; Nr=8 paths are untouched. Re-run C6 under a new tag (e.g. NR16run2) and keep raw_NR16run as the record of the arm-less run. Do not re-run train_nr16.py to get there (see P0-1a): use the existing d2sx_NR16_N10000_a1.pt, which ScorePrior reads with its own sigma_tag 'NR16'.

### s7/S7-b — CONFIRMED · FIX

**주장**: A second Nr-specific guard, separate from the one 4ad41df9 relaxed at runner.py:290, still drops every Stage C diffusion arm (M-ours-dscore-C-V0/V1/V4) for Nr=16, so the C6 output has no diffusion arms.

**위치**: `conf/code/runner.py:297-302`, `conf/code/runner.py:287-291`, `conf/code/runner.py:431-434`, `conf/results/tables_D2_NR16run.txt:38-51`, `conf/logs/run_D2_NR16.log:1-5`

**방법**: Read build_point and cmd_run at HEAD. Grepped runner.py, arms.py, score.py, guard_report.py, analysis.py and common.py for Nr==8, !=8 and in (8. Read git diff 6ed0613..HEAD. Opened raw_NR16run with numpy (448 files): arm set and meta|stagec_status. CPU check: ScorePrior loads d2sx_NR16_N10000_a1.pt at Nr=16 and denoises, so this guard is the only thing stopping it.

**근거**: The second guard is runner.py:298, inside `if stagec_ckpt:` (297). Lines 298-299: `if Nr != 8:` / `sc_why = "ABSENT -- M-ours-dscore-C-* only: " + NO_SCORE`. So spc and spc1 stay None and build_our_arms creates no C-V0/V1/V4 arms. Commit 4ad41df9 changed only line 290 (`if Nr in (8, 16)`, the M-ours-dscore path, which is also empty because gate_D2.txt/LADDER.md have no PASS rows). Line 298 is byte-identical to 6ed0613. Raw files: all 448 carry meta|stagec_status = 'ABSENT -- M-ours-dscore-C-* only: n/a (no score model for this array size)'. Arms present are M-ours-bstar, M-ours-bstar-scalar, M-ours-gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp, R5-genie. No arm is diffusion. tables_D2_NR16run.txt:51 says 'arms absent ... [M-ours-dscore, M-ours-dscore-C-V0, -C-V1, -C-V4, -C-V4b]'. Misleading log lines, cosmetic only: cmd_run:431-433 still prints 'C6: M-ours-dscore -> n/a (no score model for this array size)' for any Nr != 8, and :434 probes score_prior with a hard-coded Nr=8. There are no other Nr guards in arms.py, score.py, guard_report.py, analysis.py or common.py. After the fix the path resolves: _init('NR16run') routes A.D2_FITS to gmm_fits_D2_NR16run (12 fits), and ScorePrior(Nr=16) loads and denoises on CPU.

**수정 방향(제안)**: In conf/code/runner.py:298 change `if Nr != 8:` to `if Nr not in (8, 16):` to mirror line 290. Optionally make the cosmetic lines 431-434 follow the same set. No Demo/ change. The path stays opt-in behind --stagec-ckpt, so default arm sets are unchanged. Re-running C6 BLER would need user approval (10_SPEC A5 'one run').

**반박 검토** (agree=True, → CONFIRMED): Re-read runner.py:297-302 at HEAD. Line 298 still reads `if Nr != 8:` and line 299 sets `sc_why = "ABSENT -- M-ours-dscore-C-* only: " + NO_SCORE`. The same guard was at 6ed0613:295, and `git diff 6ed0613..HEAD -- runner.py` changes only line 290 (`if Nr in (8, 16)`), so the verifier is right that 4ad41df9 left this second guard alone. Code files are clean against HEAD, and runner.py (mtime 03:11) predates the run (raw 04:04), so the raw files came from this code. I reopened all 448 raw_NR16run files. All 448 carry meta|stagec_status = 'ABSENT -- M-ours-dscore-C-* only: n/a (no score model for this array size)'. The arms present are R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-scvamp, R4-llr, R5-genie, M-ours-gmm32, M-ours-bstar and M-ours-bstar-scalar, none of them diffusion. tables_D2_NR16run.txt:51 lists M-ours-dscore and C-V0/V1/V4/V4b as absent. My own CPU check shows the guard is the only blocker: after `runner._init('NR16run')`, A.D2_FITS resolves to gmm_fits_D2_NR16run, and `runner.score_prior('D2','S2',16,4,ckpt,ntrain=10000)` returns a ScorePrior for both psd_project=False and psd_project=True (s_lo 0.032832, s_hi 0.491519). No other Nr guard exists on this path (score.load_prior:1053-1080 and arms.build_our_arms:166-182 have none). Extra nuance 1: the recorded reason 'no score model for this array size' is false, since a model exists; this is the silent-ABSENT outcome that runner.py:1035-1037 says it was built to prevent in a one-shot A5 run. Extra nuance 2: runner.py:441-443 also prints 'Stage C arms ON ... C-{V0,V1,V4}' unconditionally (run_D2_NR16.log line 4); see missed M1. Fix caveat: re-running with the same tag after the line-298 fix would produce nothing new. runner.py:346-347 returns 'exists' for every finished chunk ('FINISHED CHUNKS ARE SKIPPED'), so all 448 would be skipped. A re-run needs a new --tag, a matching gmm_fits_D2_<tag> symlink like run_nr16.sh:27, and user approval under 10_SPEC A5.

### s7/M1 — CONFIRMED · FIX (반박 agent 추가 발견)

**주장**: With --stagec-ckpt, cmd_run always logs that the Stage C diffusion arms are ON, and no fail-early check catches a cell or checkpoint combination for which build_point drops them. So the one-shot C6 run started, logged 'arms ON', and finished without them.

**위치**: `conf/code/runner.py:441-443`, `conf/code/runner.py:1034-1042`, `conf/code/runner.py:297-299`, `conf/logs/run_D2_NR16.log:4`

**방법**: Read cmd_run at HEAD (lines 424-446) and the --stagec-ckpt pre-flight (1034-1042). Compared run log line 4 with meta|stagec_status in all 448 raw_NR16run files, using numpy on CPU.

**근거**: runner.py:441-443: `if a.stagec_ckpt: print(f"[run] Stage C arms ON (10_SPEC §3b/§3c): M-ours-dscore-C-{{V0,V1,V4}} + the mandatory GMM control ...")`. This prints no matter what the per-cell Nr is. run_D2_NR16.log:4 shows exactly this line for cell C6, yet 448/448 raw files record stagec_status 'ABSENT -- M-ours-dscore-C-* only'. The pre-flight at 1035-1041 exists to stop 'the Stage C score arms would be silently ABSENT from the whole run' under 10_SPEC A5, but it checks only that the file exists. It never compares the cell's Nr with the guard at line 298, and it never compares the checkpoint's own st['Nr'] with the cell's Nr. After the S7-b fix, a mismatched checkpoint would still fail inside score.load_prior's catch-all (score.py:1078-1080) and turn silently into ABSENT.

**수정 방향(제안)**: Opt-in only, inside the existing `if a.stagec_ckpt:` block at runner.py:1034-1042. CPU torch.load the checkpoint and sys.exit if any selected cell has C.CELLS[cell]['Nr'] != st['Nr'], or has an Nr outside the set line 298 accepts. Make the print at 441-443 per-cell, reporting the actual build decision. Default runs without --stagec-ckpt are unchanged; no Demo/ change.

### s7/S7-c — CONFIRMED · FIX

**주장**: The Nr=16 score checkpoint was put into the C6 run without any gate or verification record, and run_nr16.sh enforces none.

**위치**: `conf/code/run_nr16.sh:22-29`, `conf/code/train_nr16.py:12-13`, `conf/code/train_nr16.py:48-53`, `conf/code/arms.py:56-67`, `conf/code/runner.py:1034-1042`, `conf/code/runner.py:199-225`, `conf/code/score.py:1069-1071`, `conf/10_SPEC_stageC.md:873-874`, `conf/logs/train_nr16.log:1-15`

**방법**: Grepped conf/results/gate_*.txt and conf/LADDER*.md for NR16. Read run_nr16.sh, train_nr16.py, runner.gate_verdict, the --stagec-ckpt argument handling and score.load_prior. Read logs/train_nr16.log, logs/queue.log and raw meta|stagec_gate. Listed results/ for d2_gbprime_NR16*.

**근거**: (1) No gate record: grep of results/gate_*.txt and LADDER*.md for NR16 finds 0 files. Raw meta|stagec_gate and run log line 5: 'NO GATE RECORD mentions d2sx_NR16_N10000_a1.pt -- UNVERIFIED here'. (2) Nothing enforces a gate. run_nr16.sh:23 trains, then :28-29 runs BLER with --stagec-ckpt. No gate step exists and train_nr16's exit status is never checked. runner.py:1034-1042 checks only that the file exists. score.load_prior:1069-1071 treats an explicit ckpt as 'caller override, NOT verified against the gate record'. gate_verdict (runner:199) only reports. (3) Ungated by design: 10_SPEC_stageC.md:873 says 'D1 형제가 없으므로 이 체크포인트는 UNGATED 다', and train_nr16.py:12 says the same. (4) The report-only D2 diagnostic GB' also never ran. train_nr16.log shows the checkpoint trained ('trained 1688 ep, val 2.33129e-01, stopped_by=patience') and then `FileNotFoundError: no GMM fits for D2/S2/Nr=16` at train_nr16.py:49. Cause: arms.D2_FITS defaults to results/gmm_fits_D2 (arms.py:56), which has 0 Nr16 files. The 12 fits are in gmm_fits_D2_NR16, and train_nr16.py never calls runner._init or sets A.D2_FITS. No results/d2_gbprime_NR16_*.npz exists. The pipeline carried on anyway (queue.log 04:03 → 04:07 NR16_PIPELINE_DONE). (5) In practice no BLER came from this checkpoint either, because of S7-b. Checkpoint facts: md5 08877da2db0fc3826b2fd9d04c21de53, epoch 1688, best_epoch 1668, best_val 0.233129, Nr 16.

**수정 방향(제안)**: Keep the pre-registered UNGATED label; don't invent a gate. Opt-in fixes: in train_nr16.py set `A.D2_FITS = os.path.join(C.CONF,'results','gmm_fits_D2_NR16')` before gmm_selection at line 49, then re-run only the GB' tail (CPU/GPU-light, needs approval). In run_nr16.sh add `|| { log ABORT; exit 1; }` after line 23, so a failed trainer or diagnostic stops the BLER step. Any new Nr=16 diagnostic must use a new name (handoff §1.2), not the gate_D2 file.

**반박 검토** (agree=True, → CONFIRMED): `grep -l NR16 results/gate_*.txt LADDER*.md` finds nothing (exit 1, 9 files searched). Raw meta|stagec_gate, all 448 files, reads 'NO GATE RECORD mentions d2sx_NR16_N10000_a1.pt -- UNVERIFIED here'. run_nr16.sh:22-29 runs train, then BLER, with no status check between them. runner.py:1034-1042 checks only that the file exists. score.py:1069-1071 labels an explicit ckpt 'caller override, NOT verified against the gate record'. train_nr16.log confirms the checkpoint was saved ('trained 1688 ep, val 2.33129e-01 ... stopped_by=patience') and that the run then failed with FileNotFoundError 'no GMM fits for D2/S2/Nr=16' at train_nr16.py:49 (via arms.py:91 → :79). train_nr16.py never calls runner._init or sets A.D2_FITS. arms.py:56 defaults to results/gmm_fits_D2, which holds 0 Nr16 files, while gmm_fits_D2_NR16 holds all 12 (fit_S2_Nr16_*_n10000.npz). No results/d2_gbprime_NR16_*.npz exists. Checkpoint facts check out: md5 08877da2db0fc3826b2fd9d04c21de53, epoch 1688, best_epoch 1668, best_val 0.2331286. Nuances: (a) UNGATED is pre-registered (10_SPEC_stageC.md:873-874, train_nr16.py:12-13), so the missing gate is by design. The actual defect is the unchecked trainer exit plus the missing report-only GB'. (b) The failure was hidden from the briefing file: run_nr16.sh:24 greps only 'stopped_by=…|best …', so queue.log:30 shows just 'training: stopped_by=patience' and no traceback. (c) A trainer failure before the checkpoint was saved would still have been caught by runner.py:1038-1041. The gap covers only failures after the save, which is what happened here. The fix sketch is valid: the fit file names match ntrain=10000.

### s7/S7-d — CONFIRMED · OK

**주장**: Since 4ad41df9 the NR16 checkpoint carries its own sigma_tag, and ScorePrior and gb_prime read it back, so the Nr=16 model is not measured against the frozen Nr=8 grid.

**위치**: `conf/code/score.py:875-880`, `conf/code/score.py:959-966`, `conf/code/score.py:1223-1238`, `conf/code/score.py:1076`, `conf/code/sigma.py:108-114`, `conf/code/train_nr16.py:39-45`, `conf/results/sigma_grid_D2_NR16.txt:30`, `conf/results/sigma_grid_D2.txt:37`

**방법**: Loaded the checkpoint on CPU with torch.load (keys and values). Built ScorePrior(d2sx_NR16_N10000_a1.pt, 16, 4, eye(64)) on CPU and read s_lo/s_hi. Evaluated gb_prime's tag-resolution expression. Loaded both sigma_grid npz files. Read the train log header.

**근거**: Checkpoint keys include sigma_tag='NR16' (plus Nr=16, rung 'D2SXNR1610000', split_hash 36591e7952a8a874). It is written by score.train at score.py:878 (`sigma_tag=sigma_tag`); train_nr16.py:44 passes sigma_tag=STAG='NR16'. ScorePrior at score.py:962 does `SG.load(self.st["testbed"], sigma_tag or self.st.get("sigma_tag", ""))`. The CPU check gives s_lo=0.0328324, s_hi=0.4915192 (the NR16 grid), not the frozen [0.0330622, 0.8451555]. load_prior (score.py:1076) forwards no sigma_tag, but the checkpoint fallback covers that. gb_prime at score.py:1231-1237 with sigma_tag=None calls torch.load(...).get('sigma_tag','') and gets 'NR16'. The trainer's own log confirms the training range: "sigma grid 'NR16' [3.2832e-02, 4.9152e-01] (20 pts)". Grids: frozen D2 has 20 pts, cells C1/C2, 14336 samples, nu_q 1-99% [2.1862e-03, 1.4286e+00]. NR16 has 20 pts, cell C6, 7168 samples, [2.1559e-03, 4.8318e-01]. The top sigma is 42% lower (0.4915 vs 0.8452), so the tag matters for the training range. Older Nr=8 checkpoints have no sigma_tag (d2sx_N10000_a1.pt → missing → frozen grid), so they are unchanged. Caveats: (a) ScorePrior wraps the grid load in `except Exception: s_lo, s_hi = 0.0, np.inf` (score.py:965-966), so a missing tagged grid would silently turn off out-of-grid counting instead of failing. (b) In ScorePrior the grid only feeds out-of-grid statistics, not the denoiser. (c) gb_prime has never actually run on this checkpoint (see S7-c).

**반박 검토** (agree=True, → CONFIRMED): CPU torch.load of d2sx_NR16_N10000_a1.pt gives sigma_tag='NR16', Nr=16, rung 'D2SXNR1610000' and split_hash 36591e7952a8a874. d2sx_N10000_a1.pt (Nr=8) has no sigma_tag key, so it falls back to the frozen grid, unchanged. Write path: score.py:878 `sigma_tag=sigma_tag`; training range from score.py:779 `_sigma_range(testbed, sigma_tag)`; train_nr16.py:44 passes STAG='NR16'. Read path: score.py:962 `SG.load(self.st["testbed"], sigma_tag or self.st.get("sigma_tag", ""))`. gb_prime at score.py:1232-1238 does the same fallback when sigma_tag is None. My check through the real runner.score_prior → load_prior path gave s_lo 0.0328324 and s_hi 0.4915192, the NR16 grid. Grids: frozen has 20 pts, sigma [0.0330622, 0.8451555]; NR16 has 20 pts, [0.0328324, 0.4915192]. 0.4915/0.8452 = 0.582, so the top is 41.8% lower. One small correction: the silent-fallback `except Exception: s_lo, s_hi = 0.0, np.inf` is at score.py:964-965, not 965-966. The other untagged `SG.load("D2")` / `_sigma_range("D2")` callers are Nr=8 diagnostics only (jacobian_psd_split.py:12, diag_h4_psd_indep.py:15, diag_prov_gbprime.py:25, selftest_V2/M6/V3). None of them is on the NR16 path, so the claim holds as stated.

### s7/G-1.2 — CONFIRMED · REC

**주장**: STATUS.md, PAPER_MATERIALS.md or 10_SPEC_stageC.md present a D1-sibling gate PASS as verification of the D2 checkpoint (which has no true score).

**위치**: `conf/STATUS.md:828`, `conf/STATUS.md:875`, `conf/STATUS.md:1256`, `conf/STATUS.md:1291`, `conf/STATUS.md:1315`, `conf/STATUS.md:1629`, `conf/STATUS.md:1664`, `conf/STATUS.md:1736`, `conf/STATUS.md:825`, `conf/PAPER_MATERIALS.md:905`, `conf/PAPER_MATERIALS.md:908`, `conf/PAPER_MATERIALS.md:817-820`, `conf/STATUS.md:389-391`, `conf/STATUS.md:653-660`, `conf/10_SPEC_stageC.md:126-129`, `conf/10_SPEC_stageC.md:175`

**방법**: Grepped the three docs at HEAD (git show HEAD:...) for 게이트 통과, sibling/형제, true score/참 score, verified. Read the surrounding paragraphs.

**근거**: This is wording only. No line calls the sibling PASS 'D2 true-score accuracy', and there are explicit disclaimers: STATUS.md:389 '의미하지 않는 것: D1 게이트 통과는 D2 수신기 동작을 보증하지 않는다 ... 참 score 가 D1 에만 있다'. STATUS.md:653-660 spells out the sibling link. 10_SPEC:175 lists 'D1 게이트 통과가 D2 성능을 보증한다는 주장' under 말할 수 없다. But PAPER_MATERIALS.md:819 sets its own rule: '"게이트를 통과한 D2 모델" 이라고 쓰면 안 되고, "D1 에서 게이트를 통과한 레시피로 D2 에 학습한 체크포인트" 라고 쓴다'. Several lines break that rule by calling the D2 checkpoint or run 'gate-passed' with no sibling qualifier: STATUS.md:828 and :875 '게이트 통과 모델의 결과는 tables_D2_C.txt 에 있고'. :1256 heading 'B16e4 — 게이트 통과 + 동일예산을 동시에 만족하는 첫 표'. :1291 column header 'N=1.6e5 (게이트 통과)'. :1315 '게이트 통과 모델에서도 같은 크기의 격차'. :1629, :1664 and :1736 (the last added in the 6ed0613..HEAD range) '게이트 통과 + 동일예산'. PAPER_MATERIALS.md:905 F14 headline row 'run B16e4k = 게이트 통과 + 동일예산' (its gate column says '게이트 통과 (형제)'). :908 gate column '게이트 통과' with no qualifier. The mirror case also appears: STATUS.md:825 says the D2 checkpoint d2sx_N10000_a1.pt '사전 등록 게이트에 실패했다 (GC 0.243)', although GC was measured on its D1 sibling. 10_SPEC_stageC.md itself is clean (126-129: '판정은 오직 D1 게이트가 내린다'; 873-874 marks NR16 UNGATED).

**수정 방향(제안)**: Docs-only, no code or Demo/ change. Rewrite the listed labels in STATUS.md (825, 828, 875, 1256, 1291, 1315, 1629, 1664, 1736) and PAPER_MATERIALS.md (905, 908) to the form PAPER_MATERIALS.md:819-820 prescribes, e.g. 'D1 형제(sx_N160000_D1) 게이트 PASS 레시피' and '형제 게이트 FAIL (GC 0.243, D1)'. Leave the numbers unchanged.

**반박 검토** (agree=True, → CONFIRMED): Confirmed only in the narrow, wording-level sense. I read the lines from `git show HEAD:` copies; PAPER_MATERIALS.md and 10_SPEC are clean against HEAD. STATUS.md has one uncommitted header line, so working-tree line numbers run +1 from line 4 onward (e.g. 825→826). Verified at HEAD: STATUS.md:828/875 ('게이트 통과 모델의 결과는 tables_D2_C.txt'), 1256 (heading; the qualifier appears only in body line 1260 'D1 형제 sx_N160000_D1.pt 가 GA~GD PASS'), 1291, 1315, 1629, 1664 and 1736. PAPER_MATERIALS.md:905 has '게이트 통과 + 동일예산' with gate column '게이트 통과 (형제)', and :908 has gate column '게이트 통과' with no qualifier. These break the documents' own rule at PAPER_MATERIALS.md:819-820. The disclaimers the verifier cites (STATUS.md:389-391, 653-660; 10_SPEC:175) are real. The handoff's strong wording (§1.2: sibling PASS described as 'D2 true-score accuracy verification') is not literally present anywhere. Missed locations: PAPER_MATERIALS.md:665 'V0 는 게이트 통과에도 D2 에서 붕괴한다' (the D2 run described as gate-passed); :911 'F12 → 게이트 통과 B16e4'; :904 '게이트 통과 예산' (budget-level, borderline). 10_SPEC_stageC.md is not fully clean. :246 reads '모델은 게이트 통과 체크포인트만 쓴다. 즉 N'=1.6e5 (GA/GB/GC/GD 전부 PASS)' in the V4 definition, which covers the D2 run, and :874 reads '게이트 통과 주장은 C2(Nr=8)에만 쓴다'. figures_stagec2.py:246 has the caption title 'GATE-PASSING checkpoint', although GATE_LINE_PASS at :60-61, used at :293, carries the sibling qualifier. STATUS.md:825, the mirror case, uses the same shorthand. Its GC 0.243 is the N=1e4 row of the gate ladder (STATUS.md:76, :83 '10,000 (arm 예산) | 0.0117 | 0.243 | 0.161 | FAIL'), which is measurable only on D1.

### cost/P0-2a — CONFIRMED · FIX

**주장**: bench_moduleH.py times both priors through denoise_full(q, nu), but the headline GMM arm (M-ours-bstar) never calls denoise_full. Once per outer iteration it calls GMMPriorB.ep_site(G, b, lam_min), a mixture-EP site built from the colored likelihood. So the benchmark times the wrong GMM function.

**위치**: `conf/code/bench_moduleH.py:1-14`, `conf/code/bench_moduleH.py:49-56`, `conf/code/bench_moduleH.py:75-79`, `conf/code/arms.py:18-38`, `conf/code/arms.py:41-51`, `conf/code/arms.py:113`, `conf/code/arms.py:163`, `conf/code/arms.py:169`, `conf/code/arms.py:185`, `Demo/t2_route_a.py:277`, `Demo/t2_route_a.py:339-378`, `Demo/t2_gmm.py:44-66`, `Demo/t2_gmm.py:77-81`, `Demo/t2_gmm.py:101-122`, `conf/code/score.py:970-1001`, `conf/code/runner.py:122-128`, `conf/code/runner.py:262-306`, `conf/code/runner.py:373`, `conf/10_SPEC_stageC.md:825-832`

**방법**: Read the full call chain at HEAD: runner.build_point -> arms.build_our_arms/route_a -> RouteA/RouteAClip.run -> the prior's methods. git diff 6ed0613..HEAD does not touch bench_moduleH.py, arms.py or anything in Demo/, so the same holds at the base commit. Opened the headline raw file (raw_B16e4k/...snr-3_skip0_n40.npz). Ran a single-thread CPU timing on the real fit files and checkpoint (scratchpad t_ep.py / t_sp.py).

**근거**: Arm configs (arms.py:34-38, 18-33). 'gmm_site' = mode='colored', scal='site', hsite='scalar', lam_min=LAM_MIN=1e-6, exact_prior=True. 'score' = mode='scalar', scal='belief', hsite='matrix'. LOOP sets n_inner=1.

M-ours-bstar = route_a(*a, hp[bstar].view('eta'), code, Xp, 'gmm_site'). clip is None, so the class is plain RouteA (arms.py:44). RouteA.__init__:277 sets exact_prior = exact_prior and hasattr(prior,'ep_site'), which is True. Each outer iteration t in run() does:
- _sites(Y, Xbar, Tau, eh2), then G=A.sum(0), b=B.sum(0) (:344-345)
- use_scalar=False because mode is 'colored' (:346), so the else branch runs (:372-374): 'Lam, site_vec = self.prior.ep_site(G, b, self.lam_min); P = Lam + G'
- GMMPriorB.ep_site (t2_gmm.py:54-66): tilted_moments forms K batched NxN inverses of covinv+G plus a batched slogdet (:47-49), then inv(Cov) and eigh(Lam), with a clip-and-solve when needed
- Sigma=inv(P), hpost (:378)
- L_X over Td columns with LOO inv(P - A[c]) (:386-408), then the BCJR decode
No denoise() or denoise_full() call is made on this path. Corroboration: runner.stats_obj (:125-128) returns the GMM prior only when rx.exact_prior is True, and the headline raw file's 'M-ours-bstar|clip' has mean clip_frac 0.811 > 0. So ep_site's n_site/n_clip counters did run in B16e4k.

R2-ours-G = route_a(..., Cs, 'gaussian'), with exact_prior=False. The same colored branch gives 'P = self.prior.Cinv + G; site_vec = 0' (:376). There is no Module H call at all, only closed form.

Diffusion V1 = M-ours-dscore-C-V1 = route_a(*a, score_prior_v1, code, Xp, 'score', clip='eta'), class RouteAClip, where score_prior_v1 is a ScorePrior with psd_project=True (runner.py:302). Each outer iteration does:
- _sites, G, b
- use_scalar=True (init_colored=0). The belief branch (:360-368) loops n_inner=1 times: SigL=inv(I/nuE+G), hL, aL, nu_q, q, then prior.denoise(q, nu_q). That goes to ScorePrior._eval: jacrev(tweedie_real) over 64 real dimensions, plus a separate forward f(x), wirtinger, and project_psd (eigh). The result is cached under key (q.tobytes(), nu) (score.py:974-994).
- hsite=='matrix' then calls RouteAClip._matrix_site(q, nu_q, G) (t2_gmm.py:112-122): prior.denoise_full(q, nu_q) is a cache hit, followed by inv(nu J), eigh(Lam), clip, and returning Lam+G, eta.
- Sigma=inv(P), then LOO L_X, then BCJR.
So V1 does exactly one network+Jacobian evaluation per outer iteration (n_inner of them in general). On the score side, the benchmark does time the right function.

The benchmark's own docstring (bench_moduleH.py:3-5) says the receiver 'calls Module H ONCE per outer iteration ... through the identical entry point prior.denoise_full(q, nu)'. That is false for M-ours-bstar. The pre-registration asked for 'GMM(b* K 성분 mixture-EP) 대 신경망' (10_SPEC_stageC.md:825). denoise_full is only on the path of the control arm M-ours-bstar-scalar (arms.py:185), which calls GMMPriorB.denoise and then denoise_full, with no cache.

Ad-hoc timing check (CPU, 1 thread, 10-11 reps, random structured G/b, shared host, rough numbers only; ep_site cost does not depend on the input values):
- K=512 (N=1e4 fit, the one the benchmark used): ep_site 21.7 ms vs denoise_full 7.6 ms, so the real GMM call is ~2.85x the benchmarked one.
- K=1024 (headline fit, n160000): ep_site 47.0 ms vs denoise_full 25.6 ms (1.83x).
- Same session, V1 _eval: d2sx_N160000_a1.pt 60-61 ms, d2sx_N10000_a1.pt 57-69 ms.
- Resulting V1/ep_site ratio: 1.21-1.37x at K=1024, 2.65-3.14x at K=512. The file reports 4.6x.

**수정 방향(제안)**: Leave Demo/ untouched and write a new opt-in script, e.g. conf/code/bench_moduleH_ep.py. Keep the old bench_moduleH.py and complexity_moduleH.txt unchanged as the historical record, and write to a new results file.
1. Build the real arms with arms.build_our_arms, using the headline fits dir (gmm_fits_D2_B16e4k, kron K=1024) and ckpt d2sx_N160000_a1.pt.
2. Capture real (G, b) and (q, nu_q) inputs with thin wrappers in conf/code around prior.ep_site and ScorePrior._eval.
3. Time GMMPriorB.view('eta').ep_site(G, b, LAM_MIN) against ScorePrior._eval on fresh q (clear _cache before each call) plus RouteAClip._matrix_site and the belief-stage inverse.
4. Separately time the whole rx.run() for each arm on each trial. Report medians/quantiles, thread count, dtype and library versions.

**반박 검토** (agree=True, → CONFIRMED): I re-read the call chain at HEAD and the main claim holds.
- arms.py:36 sets gmm_site to mode='colored', exact_prior=True. arms.py:163 builds M-ours-bstar = route_a(hp[bstar].view('eta'), 'gmm_site'). t2_route_a.py:277 makes exact_prior True because GMMPriorB has ep_site. Since mode is 'colored', use_scalar is False (:346), so the else branch runs: :373-374 'Lam, site_vec = self.prior.ep_site(G, b, self.lam_min)'. denoise/denoise_full are never called on this path.
- bench_moduleH.py:77 times gmm.denoise_full.
- git diff 6ed0613..HEAD does not touch bench_moduleH.py, arms.py, Demo/ or the ScorePrior._eval logic.
- Raw corroboration: raw_B16e4k/...snr-3_skip0_n40.npz gives M-ours-bstar|clip[:,0] mean = 0.8109. That fraction comes from ep_site's n_site/n_clip counters (runner.py:122-128, :379).

One correction to the verifier's evidence. It says denoise_full is on the path of M-ours-bstar-scalar (arms.py:185). That is false. arms.py:185 passes hsite='scalar', so t2_route_a.py:369-370 skip _matrix_site and only GMMPrior.denoise runs (t2_route_a.py:115-118), which never calls denoise_full. The raw file agrees: M-ours-bstar-scalar|clip[:,0] = 0.0 in all 40 trials, as is C-V4 (same wiring). V1 shows 0.894. So in D2, GMMPriorB.denoise_full is on no production arm's path at all. Its only production caller is the D1 oracle M-ours-score (arms.py:165, hsite='matrix'). This makes the finding stronger.

Independent CPU timing (1 thread, median of 15 calls, scratchpad adv_cost.py):
- K=1024 headline fit: ep_site 44.8-50.1 ms, denoise_full 13.8 ms.
- K=512 N=1e4 fit: ep_site 21.5 ms, denoise_full 6.9 ms (3.1x).
- V1 _eval, d2sx_N160000_a1.pt, fresh q: 56.8-57.3 ms.
- V1 full Module-H work per outer iteration (belief-stage inv + denoise + RouteAClip._matrix_site): 57.0 ms. The extra over _eval is under 1 ms, so the docstring's 'everything else is shared' is wrong in letter but immaterial.
- Real-path V1/GMM: about 1.1-1.3x at K=1024 and about 2.65x at K=512. This is consistent with the verifier's 1.21-1.37x and 2.65-3.14x.

The verifier's K=1024 denoise_full figure (25.6 ms) is about 2x mine. Host variance on this shared machine is large (see missed M2).

### cost/P0-2b — CONFIRMED · REC

**주장**: complexity_moduleH.txt was produced at K=512 (and with the N=1e4 checkpoint), while the headline GMM is Kronecker K=1024 at N=1.6e5. The docs nonetheless quote the '4.6x' isotropic-microbenchmark figure as the arm-to-arm receiver cost ratio.

**위치**: `conf/results/complexity_moduleH.txt:1-19`, `conf/code/bench_moduleH.py:29-35`, `conf/STATUS.md:1217-1248`, `conf/STATUS.md:1655`, `conf/figs/F14_headline_C2_m3dB.txt:23-28`, `conf/figs/F14b_C2_m6dB_max_absolute_gap.txt:23-28`, `conf/figs/F14c_C2_p12dB_max_ratio.txt:23-25`, `conf/code/figure_f14.py:222-227`, `conf/results/NUMBERS_PACKAGE_2026-09-22.md:742`, `docs/EXPERIMENTS.md:21`, `conf/results/tables_D2_B16e4k.txt:47`

**방법**: Opened the results file. Grepped all .md/.txt/.py for 4.6x / complexity_moduleH. Listed conf/results/gmm_fits_D2 for S2_Nr8 fits. Read meta|kron_K and meta|stagec_ckpt from the headline raw file raw_B16e4k/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz on CPU.

**근거**: Setup recorded in complexity_moduleH.txt:
- ':2 date 2026-09-22 14:29:53'
- ':4 entry point : prior.denoise_full(q, nu) -> (m, J)'
- ':5 GMM arm : b* = kron (K = 512 components)'
- ':6 learned arm : d2sx_N10000_a1.pt (479,426 parameters)'
- ':16 mean ... GMM 17.054 ms, score V0 78.750 ms, score V1 78.113 ms', ':17 -> ... 4.6x'

The benchmark hardcodes NTRAIN=10000 and CKPT=d2sx_N10000_a1.pt (bench_moduleH.py:30-31). gmm_fits_D2/ has no kronK1024_n10000 file, so it selects K=512.

The headline raw file has meta|bstar=kron, meta|kron_K=1024, meta|ntrain=160000, stagec_ckpt=conf/ckpt/d2sx_N160000_a1.pt. So both the GMM K and the checkpoint differ from what was benchmarked.

Where 4.6x is used as a receiver/arm cost ratio:
- STATUS.md:1219-1221: '진입점은 양쪽 다 prior.denoise_full ... 이 한 번의 호출이 arm 간 복잡도 차이의 전부다'
- STATUS.md:1231: '시행당(16 반복): GMM 273 ms 대 학습 1260 ms'
- STATUS.md:1242-1246: '4.6× 는 b*=K=512 기준', '4.6× 는 학습 arm 의 상한이다'
- STATUS.md:1655: caveat row 10, 'K=1024 ... 측정하지 않았다'
- F14 and F14b captions, lines 23-28: '4.6x' plus a caveat that 'the GMM arm in THIS table is K=1024, whose mixture-EP site costs roughly twice as much, so the ratio here is nearer 2x -- but that was not measured'. That caveat describes the GMM cost as a mixture-EP site cost even though what was measured is denoise_full.
- F14c caption, lines 23-25: quotes 4.6x with no K caveat, although its own line 2 says the figure is 'at N=1.6e5 with K=1024'.
- figure_f14.py:222-227: the caption text is hardcoded.
- NUMBERS_PACKAGE:742: P12 'GMM K=512 17.1 ms, 학습 78.8 ms (4.6×)'
- docs/EXPERIMENTS.md:21: 'A8 복잡도 학습 4.6× GMM(K=512)'
PAPER_MATERIALS.md has no 4.6x (the only grep hit is an unrelated p-value 4.6e-02).

**수정 방향(제안)**: Add a doc/caption note, not an overwrite. Label 4.6x as 'isotropic denoise_full microbenchmark, K=512, N=1e4 ckpt; not the M-ours-bstar receiver path'. Do this in STATUS.md §6q A8, NUMBERS_PACKAGE P12, EXPERIMENTS memo, and the F14/F14b/F14c captions: change figure_f14.py so the A8 lines are read from the results file instead of hardcoded, and add the missing K caveat to F14c. Replace the number only after the P0-2a real-path benchmark exists.

**반박 검토** (agree=True, → CONFIRMED): What holds:
- complexity_moduleH.txt:5 says 'b* = kron (K = 512 components)'.
- bench_moduleH.py:30-31 pin NTRAIN=10000 and the N=1e4 ckpt. gmm_fits_D2/ has kron fits only up to K512_n10000.
- Headline raw meta: bstar=kron, kron_K=1024, ntrain=160000, stagec_ckpt d2sx_N160000_a1.pt.
- STATUS.md:1219-1221 frames the one denoise_full call as 'arm 간 복잡도 차이의 전부'. 4.6x is also quoted in NUMBERS_PACKAGE:742, EXPERIMENTS.md:21, and the three F14 captions at :23-25.

Corrections:
(1) The checkpoint mismatch does not affect cost. Both d2sx_N10000_a1.pt and d2sx_N160000_a1.pt carry hp {'arch':'dit','width':64,'depth':6,'heads':8,'patch':1} with 479,554 EMA state entries each (torch.load on CPU). My measured V1 _eval is about 57 ms for either. Only K matters.
(2) F14b is misattributed. It is built from raw_B1e4lo, and all 64 C2 -6 dB files have bstar=kron, kron_K=512, ntrain=1e4, stagec_ckpt=d2sx_N10000_a1.pt. That is the benchmark's own K, so F14b has no K mismatch. Instead its caption's 'The GMM arm in THIS table is K=1024' is false (see missed M1).
(3) The docs do disclose the K gap: STATUS.md:1242-1245 ('K=1024 의 실측 타이밍은 아직 없다') and :1655. What they never disclose is the wrong-function issue. Their K=1024 extrapolations ('~2.3x' at STATUS:1243, 'nearer 2x' in the F14 caption) scale denoise_full, not ep_site. My ad-hoc real-path ratio at K=1024 is about 1.1-1.3x.
(4) tables_D2_B16e4k.txt:47 says only 'b*=kron'. The file never states 1024 (0 occurrences), so K=1024 rests on raw meta (see M3).

F14c: the HEAD generator (figure_f14.py:224-227) writes the caveat unconditionally. F14c lacks it because it is stale (see M1).

### cost/M2 — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: The recorded 4.6x does not come back when bench_moduleH's own measurement is re-run with the same code, seed, K and checkpoint. The file records means only, with no spread or host load.

**위치**: `conf/code/bench_moduleH.py:39-44`, `conf/code/bench_moduleH.py:75-87`, `conf/results/complexity_moduleH.txt:10-17`

**방법**: Replayed bench_moduleH.main()'s timing loop in scratchpad adv_bench_replay.py (imports bench_moduleH for CKPT/NUS/REPS/timed, same rng seed 20260922, A.module_h_priors -> kron K=512). It does not write the results file; git status shows complexity_moduleH.txt unmodified. CPU, 1 thread.

**근거**: - Replay means: GMM denoise_full 8.98 ms, V0 56.07 ms, V1 56.15 ms, giving 6.2x / 6.3x (per-nu 5.1-6.9x).
- Recorded (:16-17): 17.05 / 78.75 / 78.11 ms, 4.6x.
- timed() times the GMM, V0 and V1 in separate consecutive blocks per nu, so load drift between blocks goes straight into the ratio. Only means are written: no median, spread, load average or library versions. The host has 192 cores shared by parallel runs (load avg at replay 2.9-8.3).
- Either way, the timed pair is the wrong GMM function (P0-2a). The real-path ratio at K=1024 was about 1.1-1.3x in my run.

**수정 방향(제안)**: In the new opt-in benchmark proposed under P0-2a:
- Interleave the arms within each rep.
- Report median/IQR over many reps plus os.getloadavg() and numpy/torch/BLAS versions.
- Leave complexity_moduleH.txt as the historical record, annotated as load-sensitive.

### cost/F14-cost — CONFIRMED · FIX

**주장**: The F14/F14b note that K=1024 inference cost was not measured still holds: no K=1024 cost measurement exists anywhere in the repo.

**위치**: `conf/STATUS.md:1245`, `conf/STATUS.md:1655`, `conf/figs/F14_headline_C2_m3dB.txt:25-28`, `conf/code/bench_moduleH.py:29-35`, `conf/code/runner.py:348`, `conf/code/runner.py:420`, `conf/code/runner.py:489-502`, `conf/logs/run_D2_B16e4k.log:6-8`

**방법**: Grepped conf/*.md, conf/results, conf/figs, docs and conf/logs for timing / 1024 / ms / perf_counter. Listed the scripts that time anything. Checked the headline raw npz for per-arm timing keys. Checked the run log format and whether any smoke 's/run' log exists.

**근거**: - bench_moduleH.py is the only Module H cost script, and it is pinned to N=1e4 fits (K=512).
- STATUS.md:1245: 'K=1024 의 실측 타이밍은 아직 없다'. STATUS.md:1655 and F14:27: 'not measured'.
- The headline raw file holds timing keys only for training/fit: meta|em_sec, meta|em_sec|M-ours-bstar, meta|em_sec|M-ours-gmm32, meta|fit_sec|M-ours-dscore-C-V*. There is no per-arm inference time.
- run_D2_B16e4k.log gives only per-chunk wall time for all ~14 arms together (e.g. '1/448 done ... (519 s)'). That confounds the arms and does not isolate Module H.
- runner cmd_smoke prints per-arm 's/run' (runner.py:501), but no log in conf/logs contains 's/run'.
- The only K=1024 timings I know of are my own ad-hoc, unrecorded check from this session: ep_site K=1024 ~46-50 ms vs V1 _eval ~60 ms, so ~1.2-1.4x. That is not a controlled benchmark and is not stored in the repo.

**수정 방향(제안)**: Covered by the P0-2a new opt-in benchmark, run on the headline B16e4k configuration (kron K=1024 fit plus d2sx_N160000_a1.pt), with separate Module H timing and full-block rx.run timing written to a new results file.

**반박 검토** (agree=True, → CONFIRMED): Confirmed as stated:
- grep of conf/code for perf_counter/time.time finds per-call Module H timing only in bench_moduleH.py, pinned to N=1e4 (K=512). The others (diag_ep_site, review_V1_receiver, diag_scale*, diag_sigma_coverage) log whole-run wall time only.
- No file in conf/logs contains 's/run' (the only per-arm timing print, runner.py:501 in cmd_smoke).
- run_D2_B16e4k.log reports per-chunk elapsed time over all 14 arms (e.g. '1/448 done ... (519 s)').
- The headline raw has only em_sec/fit_sec (training) timing keys.
- STATUS.md:1245 and F14:27 say not measured.

My own ad-hoc timings (ep_site K=1024 44.8-50.1 ms, V1 57 ms) are also not stored in the repo. They differ from the verifier's by up to 2x on some functions (denoise_full K=1024: 13.8 vs 25.6 ms), so neither can stand in for a controlled measurement.

### cost/M1 — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: The F14b caption falsely says its GMM arm is K=1024; the generator hardcodes that caveat for every raw set; F14c is stale relative to the committed generator.

**위치**: `conf/figs/F14b_C2_m6dB_max_absolute_gap.txt:23-28`, `conf/code/figure_f14.py:222-227`, `conf/code/figure_f14.py:13-15`, `conf/figs/F14c_C2_p12dB_max_ratio.txt:23-25`

**방법**: Read the caption files and the generator. Loaded meta|bstar, meta|kron_K, meta|ntrain and meta|stagec_ckpt from all 64 raw_B1e4lo/D2_C2_*snr-6_* files on CPU. Compared file mtimes and git log for fd641739.

**근거**: - The F14b caption (:25-28) says 'The GMM arm in THIS table is K=1024 ... so the ratio here is nearer 2x'.
- F14b reads raw_B1e4lo, and all 64 C2 -6 dB files give {('kron', 512, 10000.0)} with stagec_ckpt d2sx_N10000_a1.pt. That is exactly the benchmark's K and budget.
- figure_f14.py:222-227 hardcodes the A8 text including 'The GMM arm in THIS table is K=1024' with no condition. Yet its docstring (:13-15) says A8 is 'printed in the caption from ... results/complexity_moduleH.txt' and that 'Every number is read from files'.
- F14c (N=1.6e5, K=1024 per its own line 2) lacks the caveat because it is stale. F14c mtime is 23:04:14, figure_f14.py mtime is 23:07:59, F14/F14b are 23:08:01/03, and all were committed together in fd641739.

**수정 방향(제안)**: In figure_f14.py:
- Read meta|kron_K and meta|bstar from the raw set.
- Print the K caveat only when the raw set's K differs from the benchmark's K.
- Read the A8 numbers from the results file instead of hardcoding them.
Then regenerate F14/F14b/F14c captions (text only). Add the wrong-function note from P0-2b as well.

### cost/M3 — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: The headline tables file tables_D2_B16e4k.txt never states that the headline b* is K=1024. The only kron K it names is K=512 (from an embedded older gate table), so a reader cross-checking A8's K=512 against it would find a false match.

**위치**: `conf/results/tables_D2_B16e4k.txt:47`, `conf/results/tables_D2_B16e4k.txt:444`, `conf/results/tables_D2_B16e4k.txt:506`, `conf/results/tables_D2_B16e4k.txt:542`, `conf/code/analysis.py:603-604`

**방법**: Ran grep -c 1024 on the tables file and read the lines that name K. Read the analysis.py header code.

**근거**: - grep -c '1024' tables_D2_B16e4k.txt returns 0.
- Line 47: '# cell C2 ... b*=kron', with no K.
- Lines 444, 506 and 542: 'GMM b* : kron (kron K=512)' and 'b* (validation log-likelihood) = kron K=512'. These are inside TABLE D, sourced from gate_D2.txt dated 2026-09-21 07:49 (commit 86e43ef), i.e. an N=1e4-era GB' table.
- analysis.py:604 prints only meta 'bstar', never 'kron_K'. The raw meta does carry kron_K=1024.

**수정 방향(제안)**: analysis.py:603-604: add kron_K (from meta|kron_K) to the cell header line. This is additive, so default output is unchanged except for the extra field. Regenerate tables text only.

### cost/P0-3 — CONFIRMED · OK

**주장**: T_IN=5 is only the R3 BiG-AMP inner iteration count, and n_inner=1 is RouteA's L_H<->H inner loop. Changing T_IN does not affect the proposed arm.

**위치**: `conf/code/common.py:47`, `conf/code/arms.py:18-33`, `conf/code/arms.py:114`, `conf/code/arms.py:204`, `conf/code/bigamp.py:174-187`, `conf/code/bigamp.py:230-236`, `conf/code/runner.py:262-306`, `conf/code/runner.py:342-373`, `conf/code/runner.py:983`, `conf/code/runner.py:1022-1023`, `Demo/t2_route_a.py:264`, `Demo/t2_route_a.py:346-377`

**방법**: Grepped T_IN, t_in and n_inner across conf/code and Demo, read every definition and consumer, and confirmed git diff 6ed0613..HEAD adds no T_IN/n_inner changes. Read run|t_in from the headline raw file.

**근거**: T_IN:
- Defined at common.py:47 'T_IN = 5 # BiG-AMP inner iterations'.
- Consumed only in arms.py:114 'R3BiGAMP(*a, code, Xp, beta=BETA, t_in=C.T_IN)' and in bigamp.py (stored at :176, loop 'for _ in range(self.t_in): ... bigamp_iter(...)' at :232-235).
- The CLI flag --tin (runner.py:983) goes to build_point(t_in=...), which uses it only at :283-285 to rebuild R3-bigamp. t_in is not passed to build_our_arms (:305-307).
- rx.run(Y,H,u,perm,iters) takes no rng, so arms cannot couple through the trial stream.
- The headline raw file records run|t_in=5.

n_inner:
- Set in arms.LOOP (n_inner=1, :25) and pinned in SPEC_TABLE_11 (:204). It is a RouteA constructor argument (t2_route_a.py:264).
- Consumed in exactly one place: 'for _ in range(self.n_inner):' at :361, inside the scal=='belief' branch.
- No runner CLI flag exposes it (grep of runner.py finds no n_inner). The only way to change it is route_a(**over) or an edit to arms.py.

Nuance: n_inner is live only for the scal='belief' arms, i.e. M-ours-dscore*, C-V0, C-V1, C-V4 and M-ours-bstar-scalar. It has no effect on:
- M-ours-bstar and R2-ours-G: mode='colored', so use_scalar=False and ep_site / Cinv+G is computed once per outer iteration with no inner loop (:372-376).
- C-V4b: scal='site' (:352-359).
For the score arms, n_inner>1 also means n_inner network+Jacobian evaluations per outer iteration, because each inner step produces a new q and so misses the cache.

**수정 방향(제안)**: Nothing to fix for T_IN. If a proposed-receiver inner-iteration experiment is wanted:
- Add an opt-in runner flag, default 1, passed through route_a(**over) to the score arms only.
- Add it to the frozen-config guard (runner.py:1022-1030) and to cfg_dump, and count ScorePrior.n_query per trial as the call-count check.
- State that it cannot change M-ours-bstar.

**반박 검토** (agree=True, → CONFIRMED): Re-read at HEAD.

T_IN:
- Defined at common.py:47.
- Consumed only at arms.py:114 (R3BiGAMP t_in=C.T_IN), bigamp.py:174-176 (stored), and bigamp.py:231-235 ('for _ in range(self.t_in): ... bigamp_iter').
- runner.py:283-284 rebuilds only R3-bigamp when t_in != T_IN. build_our_arms (runner.py:305-307) gets no t_in.
- tests.py:11 imports T_IN but never uses it.
- The raw file records run|t_in=5.

n_inner:
- LOOP n_inner=1 (arms.py:25), pinned in SPEC_TABLE_11 (:204).
- Consumed only at t2_route_a.py:361, inside the scal='belief' branch.
- No runner flag exposes it. grep of conf/code finds n_inner only in arms.py.
- The frozen-config guard (runner.py:1022-1030) lists tin but not n_inner.

The verifier's nuance is correct. M-ours-bstar and R2-ours-G are mode='colored', so they never enter the inner loop (:346, :372-376), and C-V4b is scal='site'. Precedent for n_inner>1 exists only in historical Demo scripts (Demo/exp_0919_run.py:15, Demo/exp_0920_gmm.py:21-25, n_inner=3), not in the conf runner.

### denoiser/P1-3a — CONFIRMED · DIAG

**주장**: The DiT backbone (conf/code/arch_dit.py) does not structurally enforce global-phase equivariance D(e^{jphi}q) = e^{jphi}D(q).

**위치**: `conf/code/arch_dit.py:121-129`, `conf/code/arch_dit.py:150-160`, `conf/code/arch_dit.py:96-108`, `conf/code/score.py:382-385`, `conf/code/score.py:341-351`

**방법**: Read the code, then ran a CPU-only numeric check (scratchpad chk_p13_p14.py): 64 held-out D2 samples (train_rng stream 10), 4 phases, sigma grid k=0/10/19, on the B16e4k V0/V1 checkpoint ckpt/d2sx_N160000_a1.pt (hp: dit vp/angle w64 d6 h8), with the exact b* GMM as control.

**근거**: forward() packs [Re;Im] as 2 real channels per token (`y = x.reshape(-1, 2, self.Nt, self.Nr)...`, :153). `self.inp = nn.Linear(self.cdim, width)` (:124) mixes Re and Im with free real weights plus a bias. The blocks use real LayerNorm/GELU/adaLN and `self.out` is a real Linear with a bias, so no complex or phase structure is imposed. ScoreModel.raw only wraps the net with M, the real embedding of the complex-linear DFT (score.py:341-351, 385). M commutes with a global phase, so it neither breaks nor restores the property. Nothing symmetrises over phase anywhere. Measured median relative equivariance error ||e^{-jphi}D(e^{jphi}q)-D(q)||/||D(q)||: 8.3e-3 / 2.25e-2 / 4.5e-2 (max 1.3e-2 / 4.1e-2 / 8.6e-2) at sigma = 0.033 / 0.182 / 0.845. For comparison, the denoising error medians are 2.9e-2 / 0.145 / 0.649, so the phase error is about 29% / 16% / 7% of the denoising error. The exact GMM control gives 1e-16 to 2.6e-15. Git diff 6ed0613..HEAD does not touch arch_dit.py.

**수정 방향(제안)**: Opt-in and default-preserving: add a report-only phase-averaging wrapper, e.g. ScoreModel.raw averaging R^{-1} net(R x) over a few phases behind an hp flag that is absent by default, as a separate arm with its extra Jacobian cost recorded. Or train with the P1-3b augmentation. Existing checkpoints and arms stay unchanged. No Demo/ edits needed.

**반박 검토** (agree=True, → CONFIRMED): I re-read arch_dit.py:111-160 at HEAD. forward() packs [Re;Im] as channels (:153). `self.inp = nn.Linear(self.cdim, width)` (:124) plus the learned `pos` table (:125), real LayerNorm/GELU/adaLN blocks (:96-108) and `self.out` with bias (:129) give no complex or phase structure. ScoreModel.raw (score.py:382-385) only wraps with M = real embedding of the unitary DFT (score.py:341-351), which commutes with a global phase. The VP input scaling sqrt(abar) is a real scalar. ScorePrior._eval (score.py:970-994) adds no symmetrisation. I checked provenance with raw_B16e4k meta|stagec_ckpt = ckpt/d2sx_N160000_a1.pt (V0/V1/V4/V4b all share it) and ckpt hp = dit vp/angle w64 d6 h8, epoch 1784. My own CPU check (48 fresh D2 samples, rng 12345, 6 random phases, 5 sigma points) gave median ||e^{-jphi}D(e^{jphi}q)-D(q)||/||D(q)|| = 7.9e-3 / 1.4e-2 / 2.1e-2 / 2.9e-2 / 4.0e-2 at sigma 0.033 / 0.078 / 0.182 / 0.427 / 0.845. As a ratio to the denoising error that is 0.27 / 0.23 / 0.15 / 0.08 / 0.07. This independently reproduces the verifier's 8.3e-3 / 2.25e-2 / 4.5e-2 and 29% / 16% / 7%. git diff 6ed0613..HEAD does not touch arch_dit.py or arms.py.

### denoiser/P1-3b — CONFIRMED · DIAG

**주장**: The shared training loop (score.train) and the D2 data pipeline apply no global-phase augmentation to h and the noise.

**위치**: `conf/code/score.py:653-664`, `conf/code/score.py:778-781`, `conf/code/score.py:843-850`, `conf/code/arms.py:83-86`, `conf/code/d2.py:133-140`, `conf/code/param_edm.py:138-145`

**방법**: Read score.train and training_split. Grepped all conf/code/*.py for augment/rotate/rotation/global phase/equivar/np.exp(1j/torch.polar, and listed every training entry point.

**근거**: The training set is a fixed deterministic split (`X = A.training_set(...)`; `perm = np.random.default_rng(SEED_SPLIT).permutation`, :653-664), converted once to `tr = torch.as_tensor(np_pack(Xtr))` (:781). Each step does `b = tr[idx[i:i + hp["batch"]]]` (:846), `e = torch.randn(len(b), dim, generator=g)` (:849), `dsm = model.loss(b, s, e)` (:850), and applies no rotation to b or e. edm_loss does the same (param_edm.py:144). Every trainer calls score.train: runner.py:626, run_d2_sx.py:33, train_nr16.py:42, run_d2_V2.py:61, run_V3.py:68, hpo.py:121/289, run_B3.py:19, run_samplecx.py:19, run_d1_variant.py:59. The grep's only phase hits are the D2 generator's independent per-path phases `psi = 2*pi*rng.random((n, L_MAX))` (d2.py:139-140) and figure labels. So the prior is circular in distribution, but the finite training set is never phase-augmented. The HEAD diff to score.py only adds sigma_tag.

**수정 방향(제안)**: Opt-in flag in score.train, e.g. phase_aug=False by default. When set, rotate b and e by one common e^{jphi} per sample (complex-multiply before np_pack, or the equivalent 2x2 block rotation on [Re;Im]), drawing phi from a separate generator the way gj is used, so the default stream stays bit-identical. Record the flag in the checkpoint dict. Do not mix it with angle/phase-ramp augmentation.

**반박 검토** (agree=True, → CONFIRMED): I re-read score.py:653-664 (training_split: A.training_set, then a fixed SEED_SPLIT permutation), :781 (`tr = torch.as_tensor(np_pack(Xtr))`) and :843-850. Each step is `b = tr[idx...]`, `e = torch.randn(len(b), dim, generator=g)`, `dsm = model.loss(b, s, e)`. ScoreModel.loss (score.py:433-446) and param_edm.edm_loss (:138-145) apply no rotation. I grepped every call site of model.loss/edm_loss/score.train: all training goes through score.train (runner.py:626, run_d2_sx.py:33, train_nr16.py:42, run_d2_V2.py:61, run_V3.py:68, hpo.py:121/289, run_B3.py:19, run_samplecx.py:19, run_d1_variant.py:59). No caller can inject data, because training_split is called inside train. A grep for augment/rotat/equivar/global phase/torch.polar hits only figure tick labels. The D2 generator does draw per-path uniform phases (d2.py:139-140), so the prior is circular in distribution, but the finite set is never augmented. The HEAD diff to score.py only threads sigma_tag.

### denoiser/P1-4a — CONFIRMED · DIAG

**주장**: The Module-H path forms the complex covariance as nu*J with J = 0.5[(A+D)+j(C-B)] from the real 2Nx2N Jacobian and discards K = 0.5[(A-D)+j(C+B)]. The factor conventions are correct for Cov(h|q) = nu*J under CN(0, nu I).

**위치**: `conf/code/score.py:595-600`, `conf/code/score.py:975-994`, `conf/code/score.py:160-167`, `conf/code/score.py:63-73`, `conf/code/score.py:589-592`, `Demo/t2_gmm.py:112-114`, `Demo/t2_route_a.py:309-311`

**방법**: Read the conversion code, grepped for pseudo/improper/widely/(A-D) (the only hit was the LLR pseudo-observation test), and ran two CPU checks. (1) An exact improper linear-Gaussian toy in the real domain (N=5, arbitrary real prior covariance S), comparing score.wirtinger against the exact complex covariance and pseudo-covariance. (2) r_P = ||K||_F/||J||_F on d2sx_N160000_a1 and on the exact GMM (b*=kron K=512, N=1e4 fit), with n=16 and sigma k=0/10/19.

**근거**: `wirtinger`: `a,b = Jr[:n,:n], Jr[:n,n:]; c,d = Jr[n:,:n], Jr[n:,n:]; return 0.5*torch.complex(a + d, c - b)` (:597-600). ScorePrior._eval: `x = torch.as_tensor(np_pack(q))` with packing [Re;Im] (:160-167, 980), `f = tweedie_real(model, v, sg)` = x + sigma^2 s with sigma = sqrt(nu/2) (:63-66, 589-592), `Jr = torch.func.jacrev(f)(x)` (:983), `J = wirtinger(Jr)` (:985), `SigH = nu * J` (:986, used only for herm_res). The receiver builds `SigH = nu_q * J` itself (t2_gmm.py:114). K is never formed anywhere. Toy check: |nu*wirtinger(J_R) - Cov_c|/|Cov_c| = 8.8e-16, |nu*K - PCov_c|/|PCov_c| = 1.7e-15, max|Cov_R - sigma^2 J_R| = 3.7e-16. So the packing, the nu = 2 sigma^2 factor and the Wirtinger signs are all correct, and the handoff formulas hold. On the trained net, median r_P (max) is 0.30 (0.51) / 0.47 (0.83) / 0.51 (0.54) at sigma = 0.033 / 0.182 / 0.845. The exact GMM gives 9.8e-5 (0.074) / 0.021 (0.51) / 0.34 (0.55). So at low sigma the net's K is mostly spurious, while at high sigma a real posterior pseudo-covariance exists even for the circular GMM. At sigma = 0.845, lmin(Herm J) = +8.6e-4 but lmin(sym J_R) = -1.5e-2: PSD of the proper projection does not certify the real/augmented covariance. The only HEAD diff to score.py is sigma_tag, and Demo/ is unchanged.

**수정 방향(제안)**: Opt-in only (P2-A). Add an optional ScorePrior method that also returns K (0.5*complex(a-d, c+b)), or the real (nu/2)*sym(J_R), behind a new flag with default off. Consume it only in a new receiver class under conf/code, never by editing Demo/t2_gmm.py. First use: a report-only r_P diagnostic on receiver queries.

**반박 검토** (agree=True, → CONFIRMED): The code reading holds. wirtinger is `0.5*torch.complex(a + d, c - b)` (score.py:595-600), with [Re;Im] packing (:160-167) and tweedie_real = x + sigma^2 s, sigma = sqrt(nu/2) (:63-66, :589-592). _eval uses jacrev -> wirtinger at :983/:985, and the receiver builds SigH = nu_q*J itself (Demo/t2_gmm.py:114, t2_route_a.py:311). K is formed nowhere: the grep's only hit is the LLR pseudo-observation test at tests.py:303. I re-derived the linear-Gaussian toy algebra: Cov_R = sigma^2 J_R, nu*J = Crr+Cii+j(Cir-Cri), nu*K = Crr-Cii+j(Cir+Cri), so the conventions are right. My r_P on d2sx_N160000_a1 (16 fresh samples) was median 0.33 / 0.53 / 0.47 at sigma 0.033 / 0.182 / 0.845, consistent with the verifier. Two corrections. (1) The verifier's GMM control is the N=1e4 fit (kron K=512). The same-budget B16e4k b* (kron K=1024, gmm_fits_D2_B16e4k) gives r_P median 0.002 / 0.127 / 0.306 (max 0.26 / 0.52 / 0.36), so the conclusion is unchanged. (2) 'lmin(Herm J) = +8.6e-4 at sigma 0.845' depends on the sample. The repo's own n=128 record for this exact checkpoint (results/diag/jacobian-psd_D2_N160000_final.npz, the epoch-1784 final) has frac_lmin_c_neg 0.078 at sigma 0.845. It also has frac_lmin_r_neg 0.297 at the same sigma, so the verifier's point that proper-PSD does not certify the real covariance is robust. My n=32 check found 22% of samples with Herm J PSD but sym J_R indefinite at sigma 0.845. Note also that the GMM path drops pseudo-covariance too (see missed M1).

### denoiser/M1 — CONFIRMED · DIAG (반박 agent 추가 발견)

**주장**: The GMM Module-H path also drops the posterior pseudo-covariance. So the J-only proper projection is common to the learned and GMM arms, and a widely-linear fix applied only to the score arm would mix the adapter gain with the prior gain.

**위치**: `Demo/t2_gmm.py:43-52`, `Demo/t2_gmm.py:77-82`, `conf/code/score.py:503`

**방법**: Read tilted_moments and denoise_full. Ran a CPU r_P = ||K||_F/||J||_F check via score.ExactGMMTorch on the same-budget B16e4k b* (A.D2_FITS routed in-process to results/gmm_fits_D2_B16e4k -> kron K=1024), 16 fresh D2 samples, sigma k=0/10/19.

**근거**: tilted_moments forms only `Cov = einsum(w,Sig) + (mu.T*w) @ mu.conj() - outer(m, m.conj())` and returns its Hermitian part. denoise_full does the same (`Cov = X X^H + (mk.T*w) @ mk.conj() - outer(m, m.conj())`). The mixture pseudo-covariance sum_k w_k mu_k mu_k^T - m m^T is never formed (component pseudo-covariances are zero because the components are proper). It is not small: the exact same-budget GMM has r_P median 0.002 / 0.127 / 0.306 (max 0.26 / 0.52 / 0.36) at sigma 0.033 / 0.182 / 0.845.

**수정 방향(제안)**: For any P2-A work: add a conf/code subclass or adapter of GMMPriorB that also returns pseudo = (mu.T*w) @ mu.T - outer(m, m), behind an opt-in flag defaulting to off, and feed it to the same new real/augmented receiver class as the score arm. Demo/t2_gmm.py stays untouched.

### denoiser/P1-4b — CONFIRMED · DIAG

**주장**: V1's project_psd is applied to the dimensionless Wirtinger J (not to nu*J), with floor LAM_MIN=1e-6 and lmax uncapped. EP-site precision clipping is a separate later step.

**위치**: `conf/code/score.py:603-619`, `conf/code/score.py:987-998`, `conf/code/common.py:48`, `conf/code/arms.py:37`, `conf/code/arms.py:169`, `conf/code/runner.py:302`, `Demo/t2_gmm.py:112-122`

**방법**: Read the code path. Computed the EP-site clip counters (`<arm>|clip`, runner.py:379/407) from all 448 raw_B16e4k npz files (CPU), and measured J eigenvalues on d2sx_N160000_a1 (n=16).

**근거**: `J = project_psd(J) if self.psd_project else 0.5 * (J + J.conj().T)` (score.py:992) runs on J before any nu scaling. project_psd takes the Hermitian part, then `(V * np.maximum(w, lam_min)) @ V.conj().T` with lam_min = C.LAM_MIN = 1e-6 (common.py:48), and 'lmax is NOT touched' (:603-619). V1 is built with psd_project=True (runner.py:302). The receiver then forms SigH = nu_q*J and applies a second, separate clip: Lam = SigH^-1 - I/nu floored at lam_min = LAM_MIN (arms.py:37) with clip='eta' (arms.py:169; t2_gmm.py:112-122). The cavity is isotropic and nu > 0 is a scalar, so flooring J at 1e-6 equals projecting the proper posterior covariance nu*J with floor nu*1e-6. That is a PSD projection of the complex/proper covariance, never of the real 2Nx2N covariance. A floored direction gets site precision (1/nu)(1e6 - 1), about 1e6/nu. The alphaH used in D-13 is also taken from the projected J (`return m, float(np.trace(J).real / self.N)`, :996-998), so V1 changes D-13 as well as D-14. No counter records how often the floor fires (only herm_res). Measured frac lmin(Herm J) < 0 on the V0/V1 ckpt: 0.88 / 0.62 / 0.00 at sigma = 0.033 / 0.182 / 0.845, with lmax up to 1.2 / 1.88 / 1.61. Because lmax > 1 is uncapped, the site clip still fires in V1. Across B16e4k, the mean fraction of clipped site calls for M-ours-dscore-C-V1 at -3 / 0 / 3 / 6 / 9 / 12 / 15 dB is 0.908 / 0.869 / 0.827 / 0.767 / 0.725 / 0.702 / 0.689, with median relative mean shift 1.1e-3 to 4.2e-5. For comparison, M-ours-bstar (ep_site) is 0.798 to 0.459 and V0 is 0.98 to 1.0 with shift 1.4 to 35. Note that the diagnostic psd1e-2 arm used the box [1e-2, 1], which is not V1.

**수정 방향(제안)**: Keep V1 as is. Opt-in: add a projection counter to ScorePrior (a count of floor hits and the floored eigenmass), logged via query_stats. For P2-C, a variant floor (e.g. relative to nu, or 1e-2) should be a new psd_project mode, never a change to the default.

**반박 검토** (agree=True, → CONFIRMED): The code claims hold. score.py:992 runs `J = project_psd(J) if self.psd_project else 0.5*(J+J^H)` on the dimensionless J, after SigH = nu*J at :986, which is used only for herm_res. project_psd (:603-619) floors eigenvalues of Herm(J) at C.LAM_MIN = 1e-6 (common.py:48) and leaves lmax alone. V1 is built with psd_project=True (runner.py:302) and wired with clip='eta' (arms.py:169). The site clip on Lam at lam_min = LAM_MIN (arms.py:37, 'score' Module H) is a separate step (t2_gmm.py:112-122). denoise() returns tr(projected J)/N (score.py:998), so V1 also changes D-13's alphaH. No floor-hit counter exists; ScorePrior only has n_query, n_out_of_grid and herm_res. I recomputed the clip counters from all 448 raw_B16e4k files (all C2). The V1 clip fraction is 0.908 / 0.869 / 0.826 / 0.767 / 0.725 / 0.702 / 0.689 from -3 to 15 dB, and b* is 0.798 to 0.459, both matching. Corrections to the ancillary numbers: V0's range is 0.952 to 1.000 (0.952 at +15 dB), not 0.98 to 1.0. V1's median shift peaks at 1.3e-3 at 0 dB, not 1.1e-3. The frac lmin(Herm J)<0 = 0.88 / 0.62 / 0.00 figures come from only n=16. The repo's n=128 record for this checkpoint (jacobian-psd_D2_N160000_final.npz) gives 0.81 / 0.92 / 0.078 at sigma 0.033 / 0.182 / 0.845, and frac lmax>1 0.70 / 0.90 / 0.88. My own n=16 gave 0.81 / 0.88 / 0.06. So J is indefinite in most samples up to sigma about 0.2 and in a few percent at the top of the grid, not 0% there.

### denoiser/M2 — CONFIRMED · DIAG (반박 agent 추가 발견)

**주장**: The repo already holds an n=128 measurement of Herm-J and sym-J_R PSD failure rates for the exact V0/V1 checkpoint. It contradicts the verifier's n=16 figures used in P1-4a, P1-4b and P2-Cb.

**위치**: `conf/results/diag/jacobian-psd_D2_N160000_final.npz`, `conf/code/jacobian_psd.py:87-134`, `conf/STATUS.md:177`

**방법**: Opened the npz (CPU) and printed per-sigma frac_lmin_c_neg, frac_lmin_r_neg, lmin_c and frac_lmax_c_gt1. STATUS.md:177 ties the 'final' measurement to the epoch-1784 checkpoint, the same epoch as ckpt/d2sx_N160000_a1.pt.

**근거**: diffusion: frac lmin(Herm J)<0 = 0.812 (sigma 0.033), 0.922 (0.182), 0.078 (0.845). frac lmin(sym J_R)<0 = 0.992 / 1.000 / 0.297. frac lmax(J)>1 = 0.70 / 0.90 / 0.88. The verifier reported 0.88 / 0.62 / 0.00 and 'PSD at 0.845'. My independent n=16 run gave 0.81 / 0.88 / 0.06, and n=32 at 0.845 gave 0.12, with 22% of samples Herm-PSD but sym-J_R indefinite. The robust conclusion: the proper projection is indefinite for most queries up to sigma about 0.2 and for a few percent at the top of the grid, and real-domain indefiniteness is about 4x more frequent than proper at sigma 0.845.

### denoiser/P2-Ca — CONFIRMED · DIAG

**주장**: clip='mean' already exists. No existing result compares clip='mean' vs 'eta' symmetrically on the latest same-budget B16e4k V1/GMM arms.

**위치**: `Demo/t2_gmm.py:101-122`, `Demo/t2_gmm.py:54-74`, `conf/code/arms.py:41-50`, `conf/code/arms.py:162-185`, `conf/03_SPEC_ourmodel.md:40`, `conf/results/settling_D2.txt:1-35`, `conf/results/diag/jacpsd-counterfactual_SUMMARY.txt:1-60`, `conf/code/diag_psd_cf.py:91`, `conf/code/diag_h4_jswap.py:78`, `conf/results/tables_D2_B16e4k.txt:17-21`

**방법**: Read RouteAClip and GMMPriorB.ep_site, grepped conf/ for clip='mean', and listed arm names in the first npz of every raw_* directory (CPU). Computed EP-site clip rates in raw_B16e4k.

**근거**: RouteAClip._matrix_site (score arms): after flooring Lam, 'eta' keeps `eta = SigHinv @ hH - q/nu_q`, so the belief mean (Lam_c + I/nu)^-1 (eta + q/nu) differs from hH. `if self.clip == "mean": eta = (Lam + self.I_N / nu_q) @ hH - q / nu_q` (:121) restores the denoiser-stage mean hH. GMMPriorB.ep_site (GMM arms) is the same with G in place of I/nu: `eta = (Lam + G) @ m - b` (:65), selected via .view(clip) (:71-74). The only mean-vs-eta comparisons are diagnostic probes on the ungated ckpt/d2sx_N10000_a1.pt, V0 without PSD, cell C2. At n=256 (settling_D2.txt), dscore|mean gives 0.184 / 0.039 / 0.004 / 0.004 / 0.004 / 0 / 0 and dscore|eta gives 0.824 / 0.902 / 0.895 / 0.777 / 0.664 / 0.500 / 0.332. At n=64 (jacpsd-counterfactual) the numbers are 0.047 (0 dB) and 0.000 (6 dB). There is no V1+mean arm and no GMM+mean arm. raw_B16e4k contains only V0/V1/V4/V4b/bstar/bstar-scalar/gmm32, all 'eta' (arms.py:163 `.view("eta")`, :169 clip="eta"). The spec says 'Q-34 미결이므로 바꾸지 않는다' (03_SPEC:40). The ablation would matter: in B16e4k the clip fires in 69-91% of V1 site calls and 46-80% of bstar calls.

**수정 방향(제안)**: Additive and opt-in: new arms, e.g. M-ours-dscore-C-V1-mean = route_a(..., score_prior_v1, 'score', clip='mean') and M-ours-bstar-mean = route_a(..., hp[bstar].view('mean'), 'gmm_site'), behind a new build_our_arms kwarg defaulting to off. Report them alongside the existing 'eta' arms along with the recorded |clip (fraction, shift). Demo/ needs no change because both options already exist.

**반박 검토** (agree=True, → CONFIRMED): clip='mean' exists in RouteAClip._matrix_site (t2_gmm.py:121) and GMMPriorB.ep_site (t2_gmm.py:65), selected through view() (:71-74). I scanned every npz in all raw* directories. Production arms are only bstar, bstar-scalar, V0, V1, V4, V4b and gmm32 (and M-ours-score / M-ours-dscore in older dirs). No '*mean*' arm appears at any budget. All GMM arms use .view('eta') (arms.py:162-163) and all score arms use clip='eta' (:165-183). The only mean-clip data are diagnostic: dscore|mean (jacpsd-counterfactual n=4/64/256; settling_D2.txt reproduces 0.184 / 0.039 / 0.004 / 0.004 / 0.004 / 0 / 0) and d|scorew+clipmean (h4-jswap n=4/64). All of them use ckpt/d2sx_N10000_a1.pt, V0 without PSD, and N=1e4 fits. 03_SPEC:40 freezes the clip rule. One nuance the verifier understated: the two 'mean' options preserve different quantities (see missed M3). The score-arm version restores the denoiser-stage mean hH against the isotropic cavity I/nu, after which the receiver uses P = Lam + G and hpost = (Lam+G)^-1(eta+b), which is not hH. The GMM version restores the final colored tilted mean m. So a V1-mean vs bstar-mean pair is not symmetric in what it preserves, which is exactly the caveat the handoff asks to spell out.

### denoiser/M3 — CONFIRMED · DIAG (반박 agent 추가 발견)

**주장**: clip='mean' preserves different quantities on the score arms and the GMM arms, so a V1-mean vs bstar-mean ablation is not symmetric.

**위치**: `Demo/t2_gmm.py:112-122`, `Demo/t2_gmm.py:54-66`, `Demo/t2_route_a.py:365-371`

**방법**: Read both clip implementations and the RouteA.run consumption of (P, site_vec).

**근거**: Score (RouteAClip): `eta = (Lam + I/nu_q) @ hH - q/nu_q`, which restores hH only for the isotropic-cavity belief. _matrix_site then returns `Lam + G`, and the receiver computes `hpost = inv(P) @ (site_vec + b)` with P = Lam + G. That is not hH once the colored G differs from I/nu. GMM (ep_site): `eta = (Lam + G) @ m - b`, so the final colored belief mean is exactly the tilted mean m. The handoff's P2-C warning ('Denoiser-stage mean 보존과 최종 colored receiver belief mean 보존은 같지 않을 수 있으므로') applies directly.

**수정 방향(제안)**: If mean arms are added (opt-in, new build_our_arms kwarg), record which mean each one preserves, and also log ||hpost - hH||/||hH|| for the score arm, from a conf/code wrapper and not Demo. A final-belief-preserving score variant would be a separate new arm, never a change to the 'mean' default.

### denoiser/P2-Cb — CONFIRMED · DIAG

**주장**: The recorded V2 (energy head) and V3 (asymmetry penalty) outcomes are located, and a conservative (symmetric) field does not guarantee PSD.

**위치**: `conf/LADDER_C.md:2-14`, `conf/STATUS.md:604-635`, `conf/STATUS.md:879-903`, `conf/STATUS.md:1550-1565`, `conf/results/NUMBERS_PACKAGE_2026-09-22.md:420-432`, `conf/10_SPEC_stageC.md:194`, `conf/10_SPEC_stageC.md:212-216`, `conf/code/score.py:559-566`

**방법**: Read the ladder, STATUS and numbers-package records. Searched results/diag for any V2 PSD file (none found). Ran a CPU check on ckpt/d2sx_V2_N160000_a3.pt (hp head='energy'), n=16, sigma k=0/10/19.

**근거**: V2 as recorded: D2 a1 and D1 a1 DIVERGED, D1 a2 DIVERGED, D2 a2 went NaN from epoch 88. The D1 twin a3 was trained at lr/3 and got GA 9.7e-16 / GB 4.5e-3 / GC 0.1674 FAIL / GD 0.0814 (LADDER_C.md:9, STATUS:604-615). The records attribute the failure to the GC gate plus divergence, with an explicit lr confound; they do not attribute it to PSD. The V2 D2 model (a3) is UNGATED and appears in no BLER table (NUMBERS_PACKAGE:422-432). V3 (lambda=1.0) failed GB 5.9e-2 / GC 0.3525 / GD 0.3449 (STATUS:879-903). In the lambda sweep, lambda=0.01 cuts asymmetry by 21% but makes J indefinite at sigma=0.79 on D1 (lmin -0.089, frac 0.938) (STATUS:1550-1565). No V2 PSD measurement exists in the repo. My check: asym(J_R) median 8.7e-16 / 8.7e-16 / 1.0e-15, so it is symmetric by construction. Even so, lmin(Herm J) < 0 in 16/16 samples at sigma = 0.033 (min -0.103) and sigma = 0.182 (min -0.083), and it is PSD at sigma = 0.845. So the handoff's point holds on the actual V2 D2 checkpoint. It was not, however, the recorded reason V2 failed.

**반박 검토** (agree=True, → CONFIRMED): I re-read LADDER_C.md:2-13 and the HEAD STATUS.md (git show HEAD, since the working copy is modified): lines 604-635 (V2 FAIL on GC 0.1674, lr/3 confound stated explicitly) and 879-903 (V3 lambda=1.0: GB 5.914e-2, GC 0.3525, GD 0.3449). STATUS 1550-1565 has the lambda=0.01 lmin(Jr) of -0.089 and frac 0.938 at sigma 0.79 on D1. NUMBERS_PACKAGE:420-432 says no V2/V3 arm is in any BLER table, and my raw scan confirms no V2 arm anywhere. results/ has no V2 PSD measurement: the only d2sx_V2 mention is in NUMBERS_PACKAGE, and no jacobian-psd file exists for V2. 10_SPEC:194 and :212-216 already anticipate that symmetry does not imply PSD. My CPU check on ckpt/d2sx_V2_N160000_a3.pt (hp head='energy', epoch 1282, 16 fresh samples) gave asym(J_R) of about 1e-15. Herm J was indefinite in 16/16 samples at sigma 0.033 and 0.182 (min -0.117 and -0.162), so the point is reproduced. Correction: the verifier's 'PSD at sigma = 0.845' depends on the sample. I got 2/16 indefinite there (min -3.9e-3; lmin sym J_R -3.2e-2).

### denoiser/P1-1 — CONFIRMED · DIAG

**주장**: The existing hooks (diag_ep_site.py, diag_sigma_coverage.py, diag_ep_probe.py) can already dump some receiver-trajectory quantities, with gaps against the handoff §7 P1-1 list.

**위치**: `conf/code/diag_ep_probe.py:15-28`, `conf/code/diag_ep_probe.py:63`, `conf/code/diag_ep_site.py:29-114`, `conf/code/diag_ep_site.py:121`, `conf/code/diag_sigma_coverage.py:25-36`, `conf/code/diag_sigma_coverage.py:50`, `conf/code/review_V1_receiver.py:42`, `conf/code/review_V1_receiver.py:84`, `conf/code/common.py:77-78`, `Demo/t2_route_a.py:328-381`

**방법**: Read all three hooks, plus review_V1_receiver.py, RouteA.run's log and common.KEYS_RAW/KEYS_LOG.

**근거**: What already exists: (1) RouteA.run logs per iteration nu_q, alphaH, nuE, hE_norm, nmse, tauL, alphaD (t2_route_a.py:328-381). Production runner raw keeps only KEYS_RAW (blk_err, ber, nmse, tauL_gmean, alphaD, clip fracs; common.py:77) plus the per-trial <arm>|clip (clipped-site fraction and relative shift). So production raw such as raw_B16e4k has no nu_q or alphaH. (2) diag_ep_site saves per iteration blk_err, ber, nmse, nuE, nu_q, alphaH, hE_norm, tauL_gmean, plus per-trial clip fraction/shift and failures (:84-87). It takes --ckpt (:121), but sp comes from R.score_prior with psd_project=False (:37), so there is no V1 arm, and the GMM/Chat use N=1e4 fits. (3) diag_sigma_coverage saves nu_q, nmse, alphaH, nuE, blk_err, ber and every queried nu via a wrapped denoise/denoise_full (:28-36, :111). CKPT is hardcoded to d2sx_N10000_a1.pt (:25) with no --ckpt option, and it uses the frozen D2 grid. (4) diag_ep_probe wraps _matrix_site to record per call nu, alpha = tr(J)/N, min/max eig of Herm(nu J)/nu, min/max eig of the unclipped Lam, count of eig(Lam) < 1e-6, and ||hH|| (:15-28). CK is hardcoded to d2sx_N10000_a1.pt (:63), and only dscore|scorew and gmmB|scorew are wired. (5) review_V1_receiver has a V1 arm (psd_project=True, :42) but keeps only blk_err, nmse, nu_q, alphaH (:84). Gaps against P1-1: no dump of the q vector, G/b, the posterior mean hpost or Sigma, or h_true. No real Jacobian, complex covariance matrix or pseudo-covariance (only eigen summaries). No per-iteration clip flag or magnitude (only per-trial aggregates). No record of the channel mean/cov the receiver actually used. No per-call runtime. No cavity-anisotropy metric (e.g. G spectrum or Tp<Nt nullspace). No sigma-out-of-training-range indicator outside diag_sigma_coverage. No hook targets the gate-passing N=1.6e5 checkpoint or the B16e4k fits by default. There is also no cell/iteration/trial_id metadata beyond filenames and run| keys.

**수정 방향(제안)**: One new read-only driver under conf/code, e.g. diag_traj.py, reusing diag_ep_probe.instrument-style wrapping of _matrix_site/denoise_full. It should take --ckpt, --ntrain, --sigma_tag and --psd_project, and dump per (trial, iteration) q, nu_q, G eigenvalues, b, hH, J/K (or J_R), the clip flag and shift, hpost and diag(Sigma), with h_true stored separately as diagnostic-only. Output goes only to results/diag. No Demo/ edits, and production arms are untouched.

**반박 검토** (agree=True, → CONFIRMED): Verified: diag_ep_probe instrument (:15-28) with CK hardcoded (:63); diag_ep_site keys (:87), --ckpt (:121), sp from R.score_prior with the default psd_project=False (:37) and N=1e4 fits (module_h_priors default ntrain); diag_sigma_coverage CKPT hardcoded (:25) and wrap of denoise/denoise_full (:28-36); review_V1_receiver V1 arm (:42) keeping only 4 keys (:84); KEYS_RAW (common.py:77). Production raw for V1 holds only alphaD, alphaD_clip, ber, blk_err, clip, guardH, nmse, tauL_clip_frac and tauL_gmean: no nu_q, alphaH or out-of-grid. None of the hooks has a fits/tag route, so none can reach gmm_fits_D2_B16e4k. runner.py routes A.D2_FITS itself (:109) and the diag drivers do not. Hooks the verifier missed are listed in missed M4: review_V1_receiver does take --ckpt (:118); diag_scale.py part_E (:176-218) taps the live loop; jacobian_psd.py takes --ckpt (:129) and records AWGN clip_frac/shift; ScorePrior.query_stats is printed by diag_scale.py:218 as well as diag_sigma_coverage. None of this closes the stated gaps: no q/G/b/hpost/Sigma dump, no K, no per-call runtime, no anisotropy metric.

### denoiser/M4 — CONFIRMED · DIAG (반박 agent 추가 발견)

**주장**: More receiver-trajectory hooks exist beyond the three named in P1-1, and production ScorePrior out-of-grid statistics are computed but never persisted.

**위치**: `conf/code/diag_scale.py:27`, `conf/code/diag_scale.py:176-218`, `conf/code/jacobian_psd.py:128-134`, `conf/code/review_V1_receiver.py:118`, `conf/code/score.py:1004-1012`, `conf/code/runner.py:318-333`

**방법**: Grepped conf/code for query_stats and denoise_full taps. Read diag_scale part_E and jacobian_psd argparse. Listed V1 keys in a raw_B16e4k npz.

**근거**: diag_scale.part_E patches sp.denoise_full to record per iteration (nu, ||q||^2/N, ||m||^2/N, tr(J)/N) and prints sp.query_stats() (:218), with CK hardcoded to d2sx_N10000_a1.pt (:27). jacobian_psd.py takes --ckpt and --n (AWGN held-out queries only) and stores clip_frac, shift_med and cond_c_med. review_V1_receiver takes --ckpt (:118). ScorePrior.query_stats (frac_out_of_grid, herm_res) is never called in runner.py, and raw_B16e4k M-ours-dscore-C-V1 keys are only alphaD, alphaD_clip, ber, blk_err, clip, guardH, nmse, tauL_clip_frac and tauL_gmean.

**수정 방향(제안)**: In the proposed diag_traj.py, reuse diag_scale's denoise_full tap pattern and call sp.query_stats() per trial. Optionally, opt-in, write meta|qstats|<arm> in runner.py behind a flag that defaults to off, so existing raw files stay byte-identical.

### results/R-4.1 — CONFIRMED · OK

**주장**: tables_D2_B16e4k.txt / raw_B16e4k, D2/C2 -3 dB, n=2560, N_train=160000: R2 ~0.328 (NMSE med 0.1368), M-ours-bstar 623/2560 (0.0979), V0 ~0.593 (0.1357), V1 371/2560 (0.0547), V4 ~0.154 (0.0523), R5-genie 87/2560; NMSE column is a median; the GMM is Kronecker K=1024.

**위치**: `conf/results/tables_D2_B16e4k.txt:47-47`, `conf/results/tables_D2_B16e4k.txt:64-75`, `conf/results/tables_D2_B16e4k.txt:77-92`, `conf/results/tables_D2_B16e4k.txt:241-256`, `conf/results/tables_D2_B16e4k.txt:26-45`, `conf/code/analysis.py:248-257`, `conf/raw_B16e4k/D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip{0..2520}_n40.npz`, `conf/results/gmm_fits_D2_B16e4k/fit_S2_Nr8_kronK1024_n160000.npz`

**방법**: Read table A, the per-point detail rows and the NMSE-median block. Read analysis.py _cellfield. CPU script over all 64 raw files at -3 dB (skip 0..2520, contiguous, 40 blocks each): summed blk_err[:,15], np.median(nmse[:,15]), read meta|bstar, meta|kron_K, meta|ntrain, and compared meta|ll_val|kron with the K=1024 fit file.

**근거**: Raw @16 fail counts / BLER / NMSE median: R2-ours-G 839 (0.327734) / 0.1368; M-ours-bstar 623 (0.243359375) / 0.0979; V0 1517 (0.592578) / 0.1357; V1 371 (0.144921875) / 0.0547; V4 394 (0.153906) / 0.0523; R5-genie 87 (0.033984375) / nan. Table A rows match (l.64 '0.328(0.310,0.346) ... 1.37e-01', l.69 '0.243 ... 9.79e-02', l.70 '0.593 ... 1.36e-01', l.71 '0.145 ... 5.47e-02', l.72 '0.154 ... 5.23e-02', l.75 '0.034'). Median: analysis.py:251 'nm = np.nanmedian(v["nmse"][:, it])', and docstring l.257 'NMSE_H@16 (median over ALL blocks, failed and diverged included)'. Table l.241 heading also says 'NMSE_H@16 median'. GMM: every raw file has meta|bstar='kron', meta|kron_K=1024, meta|ntrain=160000, run|iters=16. meta|ll_val|kron=-11.45917 equals ll_val of fit_S2_Nr8_kronK1024_n160000.npz (the K=512 fit is -14.636). Header l.47 'b*=kron'. Arithmetic: (623-371)/623=0.40449, (623-371)/2560=0.0984375. Caveat that could mislead a reader: Table D of the same file embeds older reports that say 'GMM b* : kron (kron K=512)' (l.444) and 'b* ... = kron K=512' (l.506). Those come from gate_D2.txt and gmm_fit_D2.txt at ntrain=10000 and are not this run's b*.

**반박 검토** (agree=True, → CONFIRMED): Re-ran all 64 raw_B16e4k -3 dB files independently. Skips are 0..2520 in steps of 40, contiguous. Every file has meta|bstar='kron', kron_K=1024, ntrain=160000, run|iters=16 and run|seed=20260926. blk_err[:,15] sums: R2 839 (0.327734), bstar 623 (0.243359), V0 1517 (0.592578), V1 371 (0.144922), V4 394 (0.153906), genie 87 (0.033984). nanmedian nmse[:,15]: 0.13676 / 0.09791 / 0.13566 / 0.05474 / 0.05232 / nan. These match table A l.64-75 and the median block l.241-256. The NMSE column is a median: analysis.py:251 'nm = np.nanmedian(v["nmse"][:, it])' in _cellfield, and the docstring at l.255-256. meta|ll_val|kron=-11.459170 equals ll_val of fit_S2_Nr8_kronK1024_n160000.npz. The K=512 fit's ll_val is -14.636. (623-371)/623=0.404494 and 252/2560=0.0984375. Neither the table nor the raw data changed after 8fb27f56. The caveat also holds: Table D l.444 'GMM b* : kron (kron K=512)' and l.506 'b* ... = kron K=512' are embedded older N=1e4 reports, not this run's b*. Side note: the means are much larger than the medians (bstar 0.1216, V0 81.6), which confirms the column must be read as a median.

### results/R-5.1 — CONFIRMED · OK

**주장**: kappa_D2(L)=2-sum_l p_l^2 with p_l ∝ exp(-l/2) gives 1.614392..1.745942 for L=3..8, and the uniform-L marginal E|z|^4/(E|z|^2)^2 = mean_L kappa(L) ≈ 1.703212; d2.py uses the profile the handoff assumes.

**위치**: `conf/code/d2.py:11-17`, `conf/code/d2.py:56-66`, `conf/code/d2.py:133-140`, `conf/code/d2.py:284-293`

**방법**: Read d2.py (profile construction, sampler, T2d derivation). CPU computation of 2-sum p^2 with l starting at 0 and at 1, and from the code's own d2._P table. Monte-Carlo marginal with the real generator: d2.D2Gen('S2',8,4).sample_vecs, 400000 blocks, pooled over entries.

**근거**: Code: d2.py:64 '_w = np.exp(-np.arange(1, _L + 1) / TAU)', TAU=2.0 (l.57), normalised '_w / _w.sum()' (l.65), so l=1..L. The start index does not matter because a constant factor exp(-1/2) cancels in the normalisation: both indexings and d2._P give L=3 1.614392, 4 1.678413, 5 1.711277, 6 1.729416, 7 1.739829, 8 1.745942. Marginal: SCALE=sqrt(NrNt) and unit-norm steering give |u_l|^2=p_l (d2.py:291-293), so E|h_ij|^2 | L = 1 for every L. The per-L variance is equal, so the marginal ratio is exactly mean_L kappa(L) = 1.703212. MC with the real generator gives 1.70264 with E|h|^2=1.00027. The handoff's averaging is the right one. Scope note: the D2 value is for antenna-pair coordinates (w=e_ij). That is enough to exhibit the mismatch with the >=2 bound of a zero-mean covariance mixture, which holds for every projection.

**반박 검토** (agree=True, → CONFIRMED): d2.py:57 TAU=2.0, l.63-65 '_w = np.exp(-np.arange(1, _L + 1) / TAU); _P[...] = _w / _w.sum()'. From d2._P, 2-sum p^2 gives [1.614392, 1.678413, 1.711277, 1.729416, 1.739829, 1.745942], mean 1.7032116. The derivation checks out. Each entry is h_ij = sum_l sqrt(p_l) e^{j(psi_l + angle phase)}, because |a_r[i]|=1/sqrt(Nr), |a_t[j]|=1/sqrt(Nt) and SCALE=sqrt(NrNt) (d2.py:131, 139-140, T2d comment l.284-291). So E|h|^2=1 for every L, and the marginal ratio is the plain mean over L. Independent MC with the real generator (D2Gen('S2',8,4).sample_vecs, 200k blocks, seed 1) gives a pooled ratio of 1.70244 and E|h|^2=0.99999. Per-entry ratios range from 1.697 to 1.710. I also checked the other side of the mismatch: Demo/t2_gmm.py:6/137 fits 'p(h) = sum_k pi_k CN(h; 0, C_k)', so the baseline really is zero-mean and the >=2 bound applies.

### results/R-5.2 — CONFIRMED · REC

**주장**: d2.py's 3GPP remarks summarize the 3GPP / Sionna TR 38.901 model as 'path (ray) gains CN given angles' => conditionally Gaussian => GMM correctly specified; this should be softened.

**위치**: `conf/code/d2.py:19-23`, `conf/05_SPEC_testbed_D2.md:23-25`

**방법**: Read the d2.py docstring. grep -i 'sionna|38.901|3gpp' over conf/*.py and *.md at HEAD, and git log -S'ionna' over conf history.

**근거**: d2.py:19-21: 'with alpha_l ~ CN (the 3GPP-style convention) H would be Gaussian GIVEN the angles, i.e. a conditionally-Gaussian mixture, and a GMM would be correctly specified. Sparse specular multipath with a deterministic power-delay profile is the physically standard mmWave model'. 05_SPEC_testbed_D2.md:23 says the same: '3GPP 계열 모델은 각도가 주어지면 α_ℓ∼CN 이라 H|angles 가 Gaussian이고 ... GMM 이 correctly specified'. The [추측, VERIFY] caveat at l.25 covers GMM favourability only, not the CN characterisation. Neither 'Sionna' nor '38.901' appears anywhere in conf at HEAD or in its git history, so the code never names TR 38.901 or Sionna. What it does is characterise '3GPP-style' generically as per-path alpha_l ~ CN, and it asserts that a (finite) GMM would then be correctly specified. Both parts are what the handoff asks to soften. From general knowledge of TR 38.901 §7.5, not verified against the document in this session: ray powers are deterministic given cluster power (P_n/M), per-ray initial phases are uniform, cluster powers carry per-cluster log-normal shadowing, and LOS adds a Ricean non-zero-mean term. So 'all ray gains independent CN' is not accurate, and continuous-angle mixtures are not finite-K GMMs.

**수정 방향(제안)**: Docstring-only edit of conf/code/d2.py:19-23 (no behaviour change, so this is not a Demo/ file and needs no opt-in). Replace it with: 'if path gains are modelled as CN given the angles (a common simplification; TR 38.901 itself uses deterministic per-ray powers with random phases, per-cluster log-normal powers and a LOS term), H is conditionally Gaussian given the angles; a continuous-angle Gaussian mixture is still not a finite-K GMM'. Also append a DECISIONS/05_SPEC note instead of rewriting l.23.

**반박 검토** (agree=True, → CONFIRMED): d2.py:19-21 reads verbatim 'with alpha_l ~ CN (the 3GPP-style convention) H would be Gaussian GIVEN the angles, i.e. a conditionally-Gaussian mixture, and a GMM would be correctly specified.' 05_SPEC_testbed_D2.md:23 says the same, and its [추측, VERIFY] caveat at l.25 is only about GMM favourability. A grep over conf/**/*.py|md|txt finds no 'Sionna' or '38.901'. The only '3GPP' hits are d2.py:19, 05_SPEC:23/25 and NUMBERS_PACKAGE quotes of 05_SPEC. The 'should soften' half does not depend on TR 38.901 details. Even if CN path gains are granted, continuous uniform angles give an infinite (continuous) mixture, so 'a GMM would be correctly specified' is false for finite K. The TR 38.901 characterisation (deterministic per-ray power with random phase, log-normal cluster power, LOS Ricean term) was not checked against the standard in this session either, so that part stays external knowledge. Under 38.901 the conditional Gaussianity is at best a CLT approximation over the rays in a cluster. The docstring-only fix is safe for provenance: only Demo/ files are hashed (common.py:186 demo_hashes), not conf/code/d2.py. The verifier missed l.21-22 ('the physically standard mmWave model'); see missed M-5.2a.

### results/M-5.2a — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: The rules file mandates a 'physically standard' framing for D2, and d2.py and PAPER_MATERIALS repeat it. This is the overgeneralisation that handoff §5.2 (last bullet) warns against, and it contradicts a retraction the project already has on record.

**위치**: `conf/01_RULES.md:77-77`, `conf/code/d2.py:21-23`, `conf/PAPER_MATERIALS.md:769-770`, `conf/results/NUMBERS_PACKAGE_2026-09-22.md:695-696`

**방법**: read + grep -rniE 'physically standard|물리적으로 표준' over conf

**근거**: 01_RULES.md:77 '**testbed 선택 근거는 "물리적으로 표준이라서"이지 "GMM에 불리해서"가 아니다.**'. d2.py:21-22 'Sparse specular multipath with a deterministic power-delay profile is the physically standard mmWave model'. PAPER_MATERIALS.md:769-770 '근거는 "물리적으로 표준"이고 조건부 Gaussian 파괴는 그 물리의 귀결'. Against that, NUMBERS_PACKAGE:695 lists as a retraction '❌ "D2 is a standard mmWave channel, so the result transfers to real deployments." — D2's defining feature is deterministic |α_l|' and points to 05_SPEC:25. So the record tells writers both to call D2 physically standard and not to. Fixed amplitude, continuous uniform angles and a fixed exp(-l/2) profile are one controlled model, not the mmWave standard.

**수정 방향(제안)**: Record/docstring only. Change the d2.py:21-22 docstring to 'a controlled sparse-specular model (fixed |alpha_l|, continuous uniform angles, fixed PDP)'. 01_RULES.md is a user-owned rules file: propose a dated note that makes the framing 'controlled model isolating the breaking of conditional Gaussianity' rather than 'physically standard', and let the user decide. Do not rewrite l.77 unilaterally.

### results/R-10.1 — CONFIRMED · REC

**주장**: The record states that the V1 tail overlapping the GMM tail by ~87% rules out score/prior improvement.

**위치**: `conf/STATUS.md:1693-1705`, `conf/STATUS.md:1717-1721`, `conf/DECISIONS.md:104-104`, `git 6ed06139 commit message`

**방법**: Read STATUS.md §'genie 까지 남은 격차의 해부', DECISIONS.md entry [2026-09-23 00:10], and the commit 6ed06139 message. grep of PAPER_MATERIALS.md and results/*.txt found no 87% claim. Recomputed the overlap from raw_B16e4k -3 dB (tail = NMSE@16 >= 0.12).

**근거**: Quotes: STATUS:1703 '남은 꼬리는 **어느 prior 에게나 어려운 같은 채널 실현**'. STATUS:1719-1721 '**측정으로 배제된 것** ... score 를 더 잘 학습 (꼬리가 prior 와 87% 무관)'. DECISIONS:104 '(3) 그 꼬리는 **GMM 꼬리와 87% 겹치고** ... → **prior 의 문제가 아니라 채널 실현의 문제** ... 결론: 데이터·성분·반복·score 품질은 전부 측정으로 배제됐다'. Commit 6ed06139: '꼬리는 GMM 꼬리와 87% 겹치고 ... 따라서 데이터/성분/반복/score 품질은 측정으로 배제되고'. Raw recomputation: V1 tail 289, GMM tail 813, overlap 250 = 86.5% (V1-only 39, GMM-only 563). V1 and GMM failures overlap 321/371 = 86.5%. Why this is overinterpretation: the same data show V1 removed 563/813 = 69% of the GMM tail, so the tail does move when prior and interface change. V1 vs bstar changes both the prior and the site (PSD-projected D-14), so the co-failure cannot separate score, calibration, cavity or loop causes. No intervention experiment is cited. The statement is unchanged at HEAD; the only STATUS additions after 6ed0613 are the L-stratification and Nr16 sections.

**수정 방향(제안)**: Record-only: append a dated correction entry to DECISIONS.md and a note under STATUS.md:1719-1721, keeping the original text. Replace 'score 품질 ... 측정으로 배제' / '꼬리가 prior 와 87% 무관' with the handoff §10.1 wording: failures concentrate on shared hard blocks, and prior/interface/calibration headroom needs an intervention experiment.

**반박 검토** (agree=True, → CONFIRMED): Quotes check out: STATUS.md:1699 '겹침 250 — V1 꼬리의 87%', l.1703 '어느 prior 에게나 어려운 같은 채널 실현', l.1719-1721 '측정으로 배제된 것 ... score 를 더 잘 학습 (꼬리가 prior 와 87% 무관)'. DECISIONS.md:104 '(3) 그 꼬리는 GMM 꼬리와 87% 겹치고 ... prior 의 문제가 아니라 채널 실현의 문제 ... score 품질은 전부 측정으로 배제됐다'. The same wording is in the 6ed06139 commit message, and git diff 6ed0613..HEAD leaves these lines untouched (the only STATUS change is +40 lines elsewhere). From raw I reproduced V1 tail 289, GMM(bstar K=1024) tail 813, overlap 250 (86.5%), V1-only 39, GMM-only 563 (69.2% of the GMM tail), and V1∩GMM failures 321/371=86.5%. Two more reasons the inference is too strong. (a) The GMM tail covers 813/2560=31.8% of all blocks, so the 87% figure measures how much of V1's tail sits inside a set 2.8x larger. That shows co-occurrence well above chance (chance ≈31.8%), which supports 'shared hard blocks', but it cannot rule out gains from a better score. (b) 'Tail 87% unrelated to the prior' misreads an overlap fraction as independence from the prior. The same data show that the prior/site change removed 69% of the GMM tail. No intervention isolates the score.

### results/M-10.1a — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: The first-pass-NMSE evidence cited next to the 87% claim (STATUS:1704-1705) labels quantile bins as round thresholds. With the literal thresholds the quoted numbers do not reproduce. The 'prior-free' first pass is R0-pilot's Gaussian LMMSE with the sample covariance.

**위치**: `conf/STATUS.md:1704-1705`

**방법**: CPU recomputation from raw_B16e4k -3 dB: V1 tail (NMSE@16>=0.12) rate and V1 failure rate inside bins of the arms' iteration-1 NMSE

**근거**: STATUS: '첫 패스 NMSE < 0.28 인 블록은 최종 꼬리비율 0.036·실패율 0.106, > 0.41 인 블록은 0.352·0.328'. With literal thresholds on R0-pilot@1 NMSE (identical for R2): <0.28 gives n=693, tail 0.038, fail 0.108; >0.41 gives n=265, 0.343, 0.321. Exact match only for quantile bins: bottom 25% (<=0.2768, n=640) gives 0.036/0.106 and top 10% (>=0.4122, n=256) gives 0.352/0.328. V1's own @1 NMSE (median 0.169) is not the source, since <0.28 then covers 2334 blocks. The first pass that is 'prior 무관' is the Gaussian pilot LMMSE with Chat from N_train=160000. It is independent of the GMM-vs-diffusion comparison but not free of a prior. Qualitatively the predictor claim holds.

**수정 방향(제안)**: Record-only: add a note that the bins are the bottom quartile and top decile of R0-pilot@1 NMSE, and that the first pass uses the sample-covariance Gaussian prior.

### results/R-10.2 — CONFIRMED · REC

**주장**: The record states that the tail's flat NMSE from iteration 8 to 16 means iterations are not a lever / the loop is stuck at a 'fixed point'; no residual/cycle/convergence diagnostic backs 'fixed point'.

**위치**: `conf/STATUS.md:1707-1715`, `conf/STATUS.md:1720-1720`, `conf/DECISIONS.md:104-104`, `git 6ed06139 commit message`, `Demo/exp_0921_analysis.py:54-59`, `conf/results/tables_D2_B16e4k.txt:88-88`

**방법**: Read the quoted record lines. Recomputed from raw: tail trajectories, per-block relative NMSE change over iterations 13-16, and the project's only trajectory classifier (exp_0921 fail_classes, BER-based) restricted to V1 failures and tail failures. Checked which per-iteration fields raw stores.

**근거**: Quotes: STATUS:1714-1715 'EP 루프가 그 블록들에서 **나쁜 고정점에 갇혀 있다.** 반복 수는 레버가 아니다'. STATUS:1720 '반복 추가 (꼬리 NMSE 평탄)' listed under '측정으로 배제된 것'. DECISIONS:104 '(4) ... (0.1853→0.1938) → **루프가 나쁜 고정점에 갇힌 것**이지 반복 부족이 아니다'. Commit: '꼬리 NMSE 는 반복 8->16 에서 개선되지 않는다(0.1853->0.1938) - 루프가 갇힌 것'. Reproduced: tail median NMSE it8/12/16 = 0.1853/0.1933/0.1938 (these are medians, which STATUS does not say; means 0.2116/0.2146/0.2173), tail BLER 0.862→0.848. Diagnostics do not support 'fixed point'. Raw stores only blk_err/ber/nmse/tauL/alphaD/clip per iteration, with no state residual and no damping or restart variants; beta=0.7 and t_in=5 are fixed (run|beta, run|t_in). Of the 289 tail blocks, only 26.3% have max relative NMSE change <1e-3 over iterations 13-16 and 41.9% <1e-2; the median relative change per iteration is 0.7-1.2%. exp_0921 fail_classes (BER exactly constant over the last 4 iterations = 'stuck'; sign-alternating = 'cyc2'): V1 failures 371 = stuck 113 / cyc2 38 / other 220, and tail failures 245 = stuck 75 / cyc2 24 / other 146. So most tail failures are neither stationary nor 2-cycles by the project's own definition. The tail is also selected on the it16 NMSE, which biases the 8→16 comparison toward 'no improvement'.

**수정 방향(제안)**: Record-only correction entry: 'at beta=0.7, t_in=5, the NMSE of blocks selected by NMSE@16>=0.12 does not improve 8→16 (medians 0.1853→0.1938); by the BER classifier 99/245 tail failures are stuck or 2-cycling, 146 are other'. Drop 'fixed point' and 'iterations are not a lever' until a state-residual diagnostic exists, e.g. logging ||h_post^(t)-h_post^(t-1)||/||h_post|| as a new opt-in raw field in conf/code (not Demo/).

**반박 검토** (agree=True, → CONFIRMED): Quotes check out: STATUS.md:1714-1715 '나쁜 고정점에 갇혀 있다. 반복 수는 레버가 아니다', l.1720 '반복 추가 (꼬리 NMSE 평탄)' and DECISIONS.md:104 (4). Reproduced exactly: tail (NMSE@16>=0.12, n=289) medians it8/12/16 = 0.1853/0.1933/0.1938, means 0.2116/0.2146/0.2173, tail BLER 0.862→0.848. The share of tail blocks with max relative NMSE change <1e-3 over the 4 steps it12→16 is 26.3%, and 41.9% for <1e-2. With exp_0921 fail_classes applied verbatim (Demo/exp_0921_analysis.py:54-60: stuck = ptp of the last 4 BERs <1e-12; cyc = 5 alternating diffs), V1 failures split 371 = 113/38/220 (matching table l.88 '4.4/1.5/8.6'%) and tail failures 245 = 75/24/146. Two further checks strengthen the verdict. (a) Selection bias is measurable: selecting the tail on NMSE@8>=0.12 (n=317) gives medians it8/12/16 = 0.1829/0.1824/0.1791, a slight improvement, so the 'gets worse' pattern partly comes from selecting on it16. (b) At the population level V1 BLER goes @8 0.169 → @16 0.145 (tables_D2_B16e4k.txt:88), so 8 extra iterations remove about 14% of failures. 'Iterations are not a lever' is therefore not even true of the fixed beta=0.7, t_in=5 setting overall. Raw keeps no state residual, so a 'fixed point' cannot be diagnosed from existing data.

### results/R-10.3 — CONFIRMED · REC

**주장**: The record calls genie failures irreducible / a bound; genie fails 87, V1∩genie fails 72, so 15 blocks are V1-success & genie-fail.

**위치**: `conf/STATUS.md:1668-1676`, `conf/DECISIONS.md:104-104`, `conf/results/tables_D2_B16e4k.txt:50-50`, `conf/08_SPEC_analysis.md:10-10`, `conf/STATUS.md:692-692`, `conf/STATUS.md:795-795`, `conf/PAPER_MATERIALS.md:639-639`, `conf/code/arms.py:117-117`, `Demo/t2_route_a.py:388-390`

**방법**: Read the record lines and the genie arm construction (arms.py -> route_a mode='genie'; Demo t2_route_a genie branch). Counted from raw_B16e4k -3 dB blk_err[:,15].

**근거**: Quotes: STATUS:1675-1676 'genie 자체 실패 87 (0.0340) 은 **채널이 완벽해도 코드가 못 푸는 블록**이다. 따라서 V1 의 0.1449 중 **0.0281 은 prior 로 줄일 수 없고**'. DECISIONS:104 '(1) V1 실패 371 중 72 는 genie 도 실패 → **0.0281 은 prior 로 못 줄인다**'. Every D2 table header (e.g. tables_D2_B16e4k.txt:50; prescribed by 08_SPEC_analysis.md:10) says 'Upper bound = genie only.'. STATUS:692/795 and PAPER_MATERIALS:639 say 'R5-genie (상한)'. Raw: genie fails 87, V1 fails 371, V1∩genie 72 (=0.028125), V1-success & genie-fail 15, V1-fail & genie-success 299. For comparison, bstar∩genie 77 and bstar-success & genie-fail 10. Implementation: arms.py:117 'route_a(..., "gaussian", mode="genie")'. t2_route_a.py:388-389 'if self.mode == "genie": Hc, R = H, self.sigma2 * self.I_Nr' is the same Gaussian-approximation symbol detector plus BCJR turbo loop fed the true H, not joint MAP. Genie BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034 (table l.92), so it is itself an iterative, suboptimal receiver. The 15 V1-only successes show that its failures are not a per-block floor. Mitigating context: NUMBERS_PACKAGE:632 already forbids 'gap to the genie bound' as a result claim, because genie pairs are UNDECIDED.

**수정 방향(제안)**: Record-only: add a correction to DECISIONS.md and a note at STATUS.md:1675-1676. Rename to 'known-channel receiver reference (same EP detector + BCJR with true H)' and replace '0.0281 은 prior 로 줄일 수 없다' with '72 blocks fail under both; 15 blocks fail only under the known-H reference'. The 'Upper bound = genie only.' header comes from 08_SPEC:10. Change it only via a dated spec note so the archived tables stay as they are; do not regenerate the old tables.

**반박 검토** (agree=True, → CONFIRMED): Quotes check out: STATUS.md:1675-1676 '채널이 완벽해도 코드가 못 푸는 블록 ... 0.0281 은 prior 로 줄일 수 없고', and DECISIONS.md:104 (1). The table header at tables_D2_B16e4k.txt:50 'Upper bound = genie only.' is prescribed verbatim by 08_SPEC_analysis.md:10. From raw: genie fails 87, V1∩genie 72, V1-success&genie-fail 15, V1-fail&genie-success 299 (0.1168). bstar∩genie is 77 and bstar-success&genie-fail 10, matching the STATUS:1668-1669 table. Implementation: arms.py:117 'route_a(..., "gaussian", mode="genie")'. t2_route_a.py:388-389 'if self.mode == "genie": Hc, R = H, self.sigma2 * self.I_Nr' then feeds the same per-column LMMSE soft-IC symbol detector (l.400-408: Kg, xhat, extrinsic pL) and the BCJR turbo loop. It is an iterative Gaussian-approximation receiver with true H, not joint MAP, and genie BLER@1/@2/@8/@16 = 0.225/0.102/0.043/0.034 (l.92). The 15 blocks where V1 succeeds and genie fails refute a per-block floor, and the additive split '0.0281 + 0.1168' is not an attribution either. The verifier missed other places that call genie (and D1's R6-exactEP) a bound; see M-10.3a.

### results/M-10.3a — CONFIRMED · REC (반박 agent 추가 발견)

**주장**: Other places in the record also call the known-channel genie receiver (and, on D1, the exact-prior EP receiver R6-exactEP) an upper bound or headroom, and the verifier did not list them.

**위치**: `conf/05_SPEC_testbed_D2.md:48-48`, `conf/00_GOAL.md:111-111`, `conf/figs/F11_bler_D2_confirmatory.txt:163-163`, `conf/code/arms.py:118-119`, `conf/STATUS.md:590-590`, `conf/PAPER_MATERIALS.md:585-585`

**방법**: grep -rnE '상한|upper bound' over conf *.md/*.txt; read arms.py R6 construction

**근거**: 05_SPEC_testbed_D2.md:48 '`exactEP-true` (oracle 상한) | 없음. 상한은 `R5-genie`만 남는다'. 00_GOAL.md:111 '| R5 genie / R6 exactEP *(D1만)* | 상한 — 남은 headroom |'. F11 caption l.163 'the upper bound is the genie only.' For R6: arms.py:119 'arms["R6-exactEP"] = route_a(*a, true_prior.view("eta"), code, Xp, "gmm_site")' is the same iterative route_a EP/turbo loop with the true-prior GMM site, not a bound. STATUS:590 and PAPER_MATERIALS:585 still say '상한 대비: V0 → R6-exactEP'. These are D1-only instruments and carry no D2 claim, but they misname a receiver as a bound in the same way.

**수정 방향(제안)**: Record-only: one dated spec note (08_SPEC/DECISIONS) renaming R5-genie to 'known-channel receiver reference (same soft-IC detector + BCJR, true H)' and R6-exactEP to 'exact-prior EP reference'. Leave archived tables and figures unregenerated.

---

## 추가 발견 (P0 수정·리뷰 중, 2026-09-23)

같은 증거 기준. 상세·조치는 `CHANGELOG_REVIEW.md`.

| id | 상태 | 분류 | 판정 |
|---|---|---|---|
| N1 | CONFIRMED | 기록만 (사용자 결정 2026-09-23) | `score.train`의 `make_model`은 초기 가중치를 torch 전역 RNG에서 명시적 seed 없이 뽑는다 (`score.py` train 내부, `make_model(rung, hp, Nr, Nt)`). 한 프로세스 한 run이면 torch 기본 seed로 재현되지만, 한 프로세스에서 여러 번 학습하면 순서에 따라 초기값이 달라진다 (selftest에서 같은 설정 두 번 학습 시 epoch 1부터 val 상이 — 0.8848 vs 0.8965). 미수정. |
| N2 | CONFIRMED → 수정 | FIX | 발산 판정 `vl > 3·best`는 best<0(L6 VAE)에서 val이 음수가 된 뒤 모든 epoch를 bad로 본다. HEAD부터 존재. 기록된 L6 run은 판정 도입(c343853c) 전 학습이라 영향 없음. |
| N3 | CONFIRMED → 수정 | FIX | 재개 시 발산 카운터 `ndiv`가 0으로 초기화 → 발산 streak 도중 중단·재개한 run이 무중단 run과 다른 epoch에서(또는 다른 판정으로) 멈춘다. HEAD부터 존재. |

> **정정 (2026-09-22 17:20 CDT = 09-23 07:20 KST, N1)**: 위의 "한 프로세스 한 run이면 torch 기본 seed로 재현된다"는 **틀렸다.** 이 torch 빌드(2.14.0+cu130)는 프로세스마다 `torch.initial_seed()`가 달라진다(두 번 실행: 472102272832343518 / 16063582425403287908; common·score import 후에도 매번 다름). 따라서 `score.train`의 초기 가중치는 **어떤 wrapper에서도 재현되지 않는다** — 기존 모든 체크포인트의 초기값은 기록되지 않은 난수다. 데이터 순서·σ·ε 스트림(`g`)과 split은 seed 고정이라 그대로 재현된다. 사용자의 '기록만' 결정은 틀린 전제에서 내려졌으므로 재확인을 요청했다.

> **사용자 결정 (2026-09-22 17:45 CDT = 09-23 07:45 KST)**: 올바른 전제(초기값은 재현되지 않음)로 다시 물은 뒤에도 **기록만 남긴다.** 코드 수정 없음. 새 학습은 `torch.initial_seed()` 와 초기 가중치 해시를 로그에 남기고(`train_ctrl.py`), 사전 등록 A1 의 비교는 "초기값 차이 포함" 으로 표기한다.
