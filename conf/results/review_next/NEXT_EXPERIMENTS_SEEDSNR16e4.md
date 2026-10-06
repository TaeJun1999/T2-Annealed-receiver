# NEXT_EXPERIMENTS_SEEDSNR16e4 — 안테나 규모 확장 새 3 셀의 시드 강건성: UMi28 C6 (Nr 16) · UMi28 C9 (Nr 32) · D2 C9 (Nr 32), 시드 a2·a3, 동일예산 N′ = 1.6e5, 판정점 3 점 (사전 등록 초안 v1)

- 작성: 2026-10-03 22:59 CDT (= 10-04 12:59 KST) 초안 v1 (Opus 5.5 서브에이전트, 브랜치 `scale`, worktree `~/t2_wtS`). 앞선 초안 작성자(중단)가 남긴 미추적 `code/run_seedsnr16e4.sh` 를 읽고 고쳐 썼다(바뀐 곳은 §1 실행 스크립트 행 끝). 다음 단계: 적대적 검토(Fable 서브에이전트; 원문 `results/review_next/prereg_reviews_seedsnr16e4/`) → v2 → **동결 커밋**(scale; `conf/DECISIONS.md` 같은 줄) → §5 + `results/scale/seedsnr_s5.txt` 커밋(= **실행 커밋 1**) → CPU BLER 1 묶음 → (D2 C9 a3 의 §3d 사다리가 닫히면) §5 추가 커밋(= **실행 커밋 2**) → 2 묶음. 동결 커밋 뒤 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- **적대적 검토 반영 (워크플로 ROUND 2)** (v1 대상 반드시 3 건 — 통계·공정성 렌즈 M1·M2, 무결성 렌즈 integ-1; 검토 문안 그대로 적용, 그 밖은 바꾸지 않음; 2026-10-03 22:59 CDT (= 10-04 12:59 KST)): **M1** → §1 시드 강건성 라벨 행 끝(사다리 한정어 `; a<s> = §3d fb<k>` 는 라벨 문자열의 일부 — 한정어 없는 "시드 강건 (3/3 (i))" 은 세 시드가 모두 시행 1 일 때만; §6·EXPERIMENTS·RESULTS 는 이 문자열 그대로; §6 에서 D2 C9 는 등록 라벨·선례 규칙 라벨을 두 열로), (S1) "붙일 수 있다" → "**붙인다**" + 한정어 판 `"(확산 시드 3/3; a<s> = §3d fb<k> 클리핑)"`, (S2) 문자열 `(2/2[; a3 = §3d fb<k>])`, §2 표에 "§3d 시행 2·3 체크포인트" 행 추가. **M2** → §3 머리말 끝에 채점 규칙(미리 고정: 예측 4–8 은 라벨 대상 태그만 채점하고 "(n/6 태그 채점)", 라벨 대상 태그가 없는 셀은 "채점 불가 (사유)" 로 합계 밖; 1–3·10–12 는 이분), 예측 7 "라벨 대상 시드 태그 모두", 예측 8 "라벨 대상 시드(a1 포함)". **integ-1** → `code/run_seedsnr16e4.sh`: 회귀 검사를 실행 커밋(묶음)마다 한 번 — `raw_U28NR16B16e4chkS` 가 완성돼 있고 `run|git` 이 HEAD 가 아니면(= 2 묶음) 태그 `U28NR16B16e4chkS2` 로 다시 돈다(앞의 chkS 링크 검사 줄을 지우고 그 판정 뒤에서 `gmm_fits_D2_$CHK` 링크를 검사), start 로그에 `chk $CHK`, 머리말 (0) 에 batch 2 문구; 문서 §1 회귀 검사 행·묶음 행 "(chkS2 포함)"·수용 (e)·비용 행(chkS 묶음마다 ≈ 0.3 h, 2 묶음 ≈ 4.7 → 5.0 h)·§4.3 링크 7 → 8 개. 작성자 검사: `bash -n` 통과; 스크립트에서 그대로 잘라 낸 `nraw`·`gitok`·새 3 줄을 scratch git 저장소·가짜 raw(`run|git` 만 든 npz)로 시험(`…/scratchpad/seedsnr/chk2test/`) — chkS raw 없음 → chkS, chkS raw 의 `run|git` = HEAD → chkS(1 묶음 재개), 다른 커밋 → chkS2 이고 chkS2 링크가 없으면 ABORT(precondition) · 있으면 통과. 스크립트는 실행하지 않았다.
- 틀: `NEXT_EXPERIMENTS_SEEDS16e4.md` §1–§3 (라벨·수용·태그 관례 — **그대로** 쓴다; `--ref-arms all` 규칙), `_SEEDS3_16e4.md` (라벨의 절대 범주 표현, 재개 보장 범위 공개, §4 시작·중단·재개 표, §5 epoch 검사, `run_seeds3_eval.sh`·`run_seeds16e4.sh`), `_SCALE16e4.md` (셀·fits·b\*·판정점·σ 격자, §1 학습 실패 행(§3d), 메모리 가드 G·수용 (k), 실행 위치·실행 커밋 규칙(결정 6·7), chk 회귀 검사, `run_scale2.sh` 의 `acc`·`kchk`·`dp`), `_C6B16e4.md` §1 학습 실패 처리·§5 (D2 C6 a1 = §3d fb2 선례), `10_SPEC_stageC.md` §3d·§6g, `01_RULES.md` §4·§5, `08_SPEC_analysis.md` §2, DECISIONS 6953d595 (§3d 시행 선택 규칙).
- **작성 시점 공개**:
  - 사용자 지시: 2026-10-03 CDT 사용자 원문 "실험을 짧게 걸리는거 먼저 하고, 그 다음에 길게 걸리는거 하자" (주 세션이 비용을 비교해 ① 이 실험(Nr 16/32 시드 강건성)을 먼저, ② N 확대를 뒤로 배정). 설계 선택은 작성자가 했고 주 세션이 검토한다(사용자 항목별 승인 아님); 사용자 확인을 권하는 항목은 §4.2.
  - 이 등록은 SCALE16e4 의 BLER 결과 전부(§6.1, 감사 §6.2), SEEDS16e4·SEEDS3_16e4 결과를 **본 뒤** 쓴다. 이 초안 작성 중 본 것: a2·a3 학습 로그의 요약 줄(epoch·val loss; 판정량 아님), D2 C9 a3 fb2 학습 로그의 마지막 줄(epoch 643; 판정량 아님). **fb3 의 로그·체크포인트는 열지 않았다**(파일 존재만 `ls` 로 봤다).
  - **a2·a3 학습은 이 등록보다 먼저, 등록 없이 끝났다**: 주 세션이 SCALE16e4 동결(09-30 14:06 CDT) 뒤·§5 커밋(10-01 13:52 CDT) 전에 빈 GPU 에 넣었다(`logs/gpu_sched.log:53–56,58,60`, 10-01 00:52–03:34 CDT 투입; DECISIONS 줄 없음; SCALE16e4 §5 기록 노트 9·11·12 가 "등록 밖" 으로 기록). 학습만이고 BLER 은 없다 — 이 셀들의 테스트 BLER(SCALE16e4 A 태그)은 학습이 끝난 뒤(10-01 14:16 CDT~) 나왔다. 시드별 시각은 **§4.1 표**.
  - **이 등록이 평가하는 체크포인트는 어느 수신기로도 평가된 적 없다**: `raw_*{NR32,NR16}*s{2,3}` 없음, `logs/run_D2_*.log`·`logs/ald_*.log` 에 `_a2`/`_a3` stem 없음(작성자 grep, `~/t2_wtS`·`~/t2`).
  - **U28NR16 a3 의 SIGINT·재개**: 주 세션이 GPU 를 비우려고 epoch 491 진행 중에 SIGINT (`gpu_sched.log:68` "aborted=True = not an attempt") → 같은 명령으로 재개(`:71`, 로그 `>>` 이어 쓰기) → 635 epoch patience 정지(`:72`). 01_RULES §5 의 재개 규칙 그대로다. **재개의 보장 범위** (SEEDS3_16e4 공개 그대로; 현재 줄 번호): `score.train` 은 model·optimizer·EMA·CPU 생성기 `g` 상태·best/best_epoch·hist 를 복원하고(`score.py` 872, 908–916) 진행 중이던 epoch 491 을 저장된 RNG 로 처음부터 다시 돈다(`:1010–1027`, 로그 506 행에 epoch 491 이 재개 구간에 한 번만 있다) → 표본 스트림은 중단 없는 실행과 같다; GPU 부동소수 비트 동일은 보장되지 않는다(결정론 설정 없음 — 중단 없는 실행의 재현에도 같은 제약).
  - **D2 C9 a3 는 발산했다**(1240 epoch, best @1235, `stopped_by=diverged`; `gpu_sched.log:74` 10-01 08:33 CDT). 주 세션이 10_SPEC §3d 로 fb2·fb3 를 GPU 0·1 에서 병렬 시작했다(`gpu_sched.log:90–91`, 10-03 18:12 CDT; 이 초안보다 먼저). 이것은 **선례(SEEDS16e4·SEEDS3 §1: 발산 시드는 사다리 없이 "학습 실패")와 다른 규칙**이고, 근거와 선례 규칙 병기는 §1 학습 실패 행에 적는다.
  - 작성자가 이미 관측된 a1 데이터에서 한 확인(새 시행 없음, scratch 출력, 단일 프로세스·GPU 숨김): (1) `raw_<T>` 의 판정점 3 점 청크만 심볼릭 링크한 디렉터리에 `analysis.main("D2", "", root=…, out_dir=…)` → 세 셀 모두 판정점과 표 B `b* → V1` 계수가 7 점 표와 같다(UMi28 C6 0/+3/+6 232:44, UMi28 C9 −3/0/+3 391:32, D2 C9 −9/−6/−3 914:29); (2) 같은 부분집합으로 `frontier_ci.py --recovery … --level 0.95` → SCALE16e4 의 R1·R1 − R2 줄(90 %·95 %)이 숫자 그대로 재현(D2 `scale2_primary_D2_L95.txt:3–6`, UMi28 S1 `scale2_step_U28_S1.txt:3–5`); (3) {V1, b\*, genie} 3 arm raw(`raw_U28NR16B16e4last`)에는 `analysis.main` 이 table A 의 기준 arm `R2-ours-G` 가 없어 `KeyError` 로 멈춘다.
- 목적: SEEDS16e4 와 같다 — "검증손실로 고른 시드 a1 이 운이 좋았던 것 아닌가" 를 SCALE16e4 의 새 3 셀(Nr 16·32)에서 묻는다. 같은 레시피·예산·GMM b\*·테스트 시행·판정점에서 확산 체크포인트만 바꾼다. SCALE16e4 의 판정(1차 (T+) 둘, 표 B (i) 셋, 𝔅 36, 2차 단계)은 어느 결과에서도 바뀌지 않는다; 산출은 **셀별 시드 강건성 라벨 3 개 + §1 문장 조건**이다.

---

## 0. 출발점 (판정에 쓰지 않는다; SCALE16e4 §6.1 전사)

| | UMi28 C6 a1 (`raw_U28NR16B16e4`, `_best` @642) | UMi28 C9 a1 (`raw_U28NR32B16e4`, `_best` @232) | D2 C9 a1 (`raw_NR32B16e4`, `_best` @230) |
|---|---|---|---|
| 판정점 (앵커 b\*, 자동) | +0/+3/+6 | −3/+0/+3 | −9/−6/−3 |
| 표 B `b* → V1` | 114:26 · 81:11 · 37:7, pooled 232:44, POWERED 3/3 → (i) | 173:13 · 136:12 · 82:7, 391:32, 3/3 → (i) | 641:16 · 198:9 · 75:4, 914:29, 3/3 → (i) |
| 판정점 실패 수 /2560: b\* · V1 · genie | 455·257·112 · 367·187·82 · 119·38·13 | 509·304·145 · 349·180·70 · 88·30·9 | 849·231·81 · 224·42·10 · 48·18·4 |
| 첫 판정점 V1 BLER@16 (95% Wilson) | +0 dB 0.143 (0.130, 0.157), 367 | −3 dB 0.136 (0.124, 0.150), 349 | −9 dB 0.087 (0.077, 0.099), 224 |
| 첫 판정점 b\* / genie | 0.178 / 0.046 | 0.199 / 0.034 | 0.332 / 0.019 |
| **R_dp** [90% paired] (`recovery_<T>.txt:8`) | **0.287** [0.253, 0.322] | **0.432** [0.402, 0.462] | **0.811** [0.790, 0.832] |
| SNR@0.1 격차 b\*−V1 [90%]: 7 점 표 / 3 점 부분집합 (작성자 확인) | +1.41 [+1.08, +1.67] / +1.41 [+1.09, +1.65] | +2.29 [+1.98, +2.61] / +2.29 [+1.99, +2.60] | +2.99 [+2.72, +3.25] / "≥ +2.76" (V1 이 −9 dB 에서 이미 0.1 아래 — censored) |
| 이 셀을 쓰는 SCALE16e4 문장 | UMi28 S1 증가 +0.137 [90% +0.085, +0.193], S2 증가 (단조 증가), "등록된 baseline 전부(13 개)와 멀어진다" | UMi28 1차 (T+) ΔR +0.282 [90% +0.232, +0.335], S2, "전부(13 개)" | D2 1차 (T+) ΔR +0.302 [95% +0.254, +0.355], D2 S2 판정하지 못함 |
| 세 시드 best val (판정량 아님) | a1 0.5224766 @642 · a2 0.5221701 @847 · a3 0.5224268 @615 | a1 0.3923236 @232 · a2 0.3914202 @446 · a3 0.3913749 @917 | a1 0.0988171 @230 · a2 0.1022046 @318 · a3 원 시행 발산(@1235 0.0959989, 평가 안 함) · a3 fb2 0.0918484 @1493 (§5·§6.1) |

- **이미 정해진 사실**: 판정점은 앵커 b\* 의 BLER 로만 정해지고 §1 수용 (b) 가 b\* 출력의 a1 비트 동일을 요구하므로, 수용된 시드 태그의 판정점은 a1 과 같다(세 셀 모두 세 점의 b\* BLER 이 [0.005, 0.9] 안 — SV8e 같은 미리 정해진 (iv) 는 없다). 작성자 확인 (1)(2) 로, 판정점 3 점만 돌려도 a1 의 판정점·표 B 계수·R_dp·ΔR/S1 줄이 7 점 결과와 같게 계산된다.
- 선례: SEEDS16e4 §6 — D2 C2 "시드 강건 (3/3 (i))", UMi28 C2 "시드 강건 (3/3 (i))" (R(3 점 합) D2 0.509/0.513/0.520, UMi28 0.150/0.162/0.178). SEEDS3_16e4 §6 — D3 3/3 (i), MIX3 3/3 (i) (보고 전용), SV8e "판정하지 못함 (0/3 (i), 3 판정 못함)" (§0 의 사실).

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **체크포인트** | UMi28 C6: `ckpt/d2sx_UMi28NR16_N160000_a{2,3}_best.pt` — `train_nr16.py --nr 16 --prior UMi28 --ntrain 160000 --sigma-tag U28NR16g --fits-tag U28NR16B16e4 --attempt 2\|3 --fallback 1 --no-gbprime` (rung D2SXUMi28NR16160000). UMi28 C9: `ckpt/d2sx_UMi28NR32_N160000_a{2,3}_best.pt` — `--nr 32 --prior UMi28 --ntrain 160000 --sigma-tag U28NR32 --fits-tag U28NR32B16e4 --attempt 2\|3 --fallback 1 --no-gbprime` (D2SXUMi28NR32160000). D2 C9 a2: `ckpt/d2sx_NR32_N160000_a2_best.pt` — `--nr 32 --ntrain 160000 --sigma-tag NR32 --fits-tag NR32B16e4 --attempt 2 --fallback 1 --no-gbprime` (D2SXNR32160000); **D2 C9 a3 는 다음 행**. 레시피·σ 격자·분할(split_hash)은 a1 과 같다(SCALE16e4 §1 V1 학습 행; §5 에서 대조). 시드 = SEED_TRAIN + rung·17 + attempt (초기화·배치 순서만 다름). **평가 가중치 = `_best.pt`** (a1 판정 태그와 같음); last 는 평가하지 않는다. sha·epoch·best_epoch·stopped_by 는 §5 에 적고 커밋한 뒤에만 BLER |
| **학습 실패 · D2 C9 a3 (§3d)** | 발산 판정은 `score.py` 규칙(val > 3·best 또는 NaN 이 5 epoch 연속). `aborted = True` (SIGINT, 또는 min_epochs 전 max_epochs)는 01_RULES §5 에 따라 시도가 아니며 같은 체크포인트에서 재개한다; max_epochs 3000 정지는 유효(C6B16e4 §1). **`stopped_by = diverged` 이면 10_SPEC §3d**: fb2 = `train_nr16.py --nr 32 --ntrain 160000 --sigma-tag NR32 --fits-tag NR32B16e4 --attempt 3 --fallback 2 --no-gbprime` (전역 기울기 노름 클리핑 1.0), fb3 = `… --fallback 3 …` (+ lr/3); 같은 rung·attempt = **같은 시드**(초기화·데이터 스트림) — 시드 축은 a3 그대로다(`train_nr16.py` docstring·`:54–65`). 체크포인트 `ckpt/d2sx_NR32_N160000_a3_fb{2,3}{,_best}.pt`. **쓰는 시행 = 번호가 가장 낮은 성공 시행**(DECISIONS 6953d595; 성공 = aborted False 이고 stopped_by ≠ diverged): fb2 가 성공하면 fb2 를 쓰고 fb3 은 그 시점에 SIGINT 로 멈추며 **열지 않는다**(sha·val·BLER 모두 읽지 않음). fb2 가 diverged 이면 fb3 (성공일 때). 둘 다 실패 → **"학습 실패 (시드 a3)"**, BLER 없음, §5 `SEED NR32B16e4s3 -`, 집계에서 "판정 못함". 쓴 시행을 §5·§6 에 적는다. 원 시행 a3 의 `_best.pt` (@1235)는 보존하되 평가하지 않는다(C6B16e4 §5 선례). UMi28 C6·C9 와 D2 C9 a2 는 모두 patience 정지라 이 행이 걸리지 않는다(§5). **선례와 다른 규칙 (공개)**: SEEDS16e4 §1·SEEDS3 §1 은 발산 시드를 사다리 없이 "학습 실패" 로 센다("시드 분포 자체를 보므로 수리하지 않는다"). 이 등록은 §3d 를 쓴다. 근거: (1) 이 셀들의 a1 을 낸 등록(SCALE16e4 §1 학습 실패 행)의 절차가 "동결 레시피 + §3d" 이고, 같은 추세의 D2 C6 a1 (`raw_NR16B16e4`) 자체가 같은 양상(시행 1 이 epoch 1064 에서 best 직후 발산)으로 만든 fb2 체크포인트다(C6B16e4 §5) — Nr ≥ 16 에서 a1 값을 낸 절차의 시드 분포를 재려면 사다리까지 포함해야 한다; (2) fb2 는 a3 의 시드에 클리핑만 더하므로 시드 축이 바뀌지 않는다; (3) 시행 선택은 미리 정한 번호 규칙이고 val loss·BLER 을 보지 않는다. 주 세션 결정(WORK_QUEUE "NR32 a3 diverged → 시드 등록 시 §3d fb2"; 사다리 학습은 이 초안 전에 시작). **선례 규칙 병기 (보고 전용)**: 선례 규칙이면 D2 C9 a3 = 학습 실패이고 D2 C9 집계는 a1·a2 의 라벨로만 정해진다 — §6 에 등록 라벨과 나란히 적되 라벨로 쓰지 않는다(이미 정해지는 값이라 선택의 여지가 없다) |
| **바뀌지 않는 것** | GMM b\*·적합(값은 `results/scale/scale2_s5.txt` CELL 줄 = SCALE16e4 §5; 스크립트가 읽는다): UMi28 C6 = `gmm_fits_D2_U28NR16B16e4` (kron 4096, ll_val 56.5879534445348), UMi28 C9 = `gmm_fits_D2_U28NR32B16e4` (kron 4096, 152.23176788511105), D2 C9 = `gmm_fits_D2_NR32B16e4` (kron 2048 — 적합 격자 내부, 242.7371088214899); 세 셀 모두 격자 full 16..512 · kron 16..4096. 링크 `results/gmm_fits_D2_<T>s{2,3}` → `gmm_fits_D2_<T>` (상대 링크, git 미추적 — 선례; 스크립트가 대상 일치를 검사). 부호 (133,171)_8, QPSK, 16 반복, n = 2560, 테스트 시행 0..2559, chunk 40 → {(40k, 40): k = 0..63} × 3 점 = 192 파일, 수신기 CPU complex128, GPU 숨김(`CUDA_VISIBLE_DEVICES=`). 시행 스트림은 (셀, prior, SNR) 로 정해지므로(`trial_rng([20260926, 2, PID, Nr, T, Tp, snr+100])`) **b\*·genie·모든 비-V1 arm 의 출력은 a1 A 태그와 비트 동일**해야 하고 판정점(앵커 b\*)도 a1 과 같다 |
| **SNR 점 = 판정점 3 점만** | UMi28 C6 0/+3/+6, UMi28 C9 −3/0/+3, D2 C9 −9/−6/−3 (SCALE16e4 §6.1 의 자동 판정점; 스크립트 상수, 손으로 고르지 않음). 근거: (1) 라벨(표 B)·R_dp·§1 문장 조건은 판정점 3 점만 쓰고, 판정점은 앵커 b\* 로 정해지며 b\* 는 수용 (b) 로 a1 과 비트 동일 → 나머지 4 점은 어떤 라벨·문장에도 들어가지 않는다; (2) 작성자 확인 (1)(2): 3 점 부분집합에서 a1 의 판정점·표 B 계수·R_dp·ΔR/S1 줄이 7 점 결과와 같다; (3) 비용 ≈ 53.4 h → ≈ 22.9 h (비용 행). 선례(SEEDS16e4·SEEDS3)는 셀 격자 7 점 전부를 돌렸다 — C2 태그당 30–90 분이라 비용 문제가 없었다. **잃는 것 (보고 전용만)**: V1 의 SNR@0.1 (D2 C9 은 V1 이 −9 dB 에서 이미 0.1 아래라 격차가 "≥" 로 censored), UMi28 C6 의 R(−3 dB), R\*@0.05·Q-OP, 판정점 밖 V1 곡선 — §6 에 n/a 로 적는다 |
| **arm = A 태그의 11 arm** | `M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp R5-genie` (V0·V4·V4b 없음 = SCALE16e4 원칙 (2)). 근거: (1) 표 B·R_dp 는 b\*·V1·genie 가 한 raw 에 있어야 한다(V1 만 돌리고 a1 raw 의 b\* 열을 빌리는 도구는 없고, 새 코드는 쓰지 않는다); (2) {V1, b\*, genie} 3 arm raw 에는 analysis 가 돌지 않는다(작성자 확인 (3)); (3) 나머지 8 arm 의 추가 비용은 SCALE16e4 실측으로 6–17 % (last 태그 {V1, b\*, genie} 3 점 44.2 / 325.1 / 266.7 분 vs A 태그 × 3/7 = 51.8 / 351.4 / 283.7 분)이고, 그 대가로 비-V1 10 arm 전부의 a1 재생이 수신기 코드·환경 회귀 검사가 된다(선례 `--ref-arms all`). 𝔅(`pair_baselines`)·PIL·ALD·last·K2 태그와 GB′ 는 돌리지 않는다(시드는 V1 만 바꾼다; 선례도 GB′·pair 없음) |
| **회귀 검사 (실행 0 단계, 게이트)** | `U28NR16B16e4chkS` = SCALE16e4 chk 명령 그대로(a1 `_best` 34136808b1e367ac, UMi28 C6 −3 dB, 청크 0 = 이미 관측된 시행 0..39, 11 arm, 워커 1)를 실행 커밋에서 다시 돌려 `eval_accept --ref-arms all` 로 `raw_U28NR16B16e4` 와 11 arm × KEYS_RAW 비트 동일을 확인한다(fits 링크 `gmm_fits_D2_U28NR16B16e4chkS` → `gmm_fits_D2_U28NR16B16e4`). **실패하면 실행 전체 ABORT → 사용자**(코드·환경 drift). 근거: 시드 태그의 `--ref-arms all` 은 V1 이 설계상 달라 V1 경로(score 네트워크·torch)의 drift 를 잡지 못한다; chk 는 a1 V1 까지 재현한다(RGB16e4chk·SCALE16e4 chk 선례). 비용 ≈ 19 분(SCALE16e4 18.8 분). **실행 커밋(묶음)마다 1 회**: 2 묶음에서는 `raw_U28NR16B16e4chkS` 의 `run\|git` 이 HEAD 가 아니므로 스크립트가 태그 `U28NR16B16e4chkS2` 로 같은 명령을 다시 돌린다(링크 `gmm_fits_D2_U28NR16B16e4chkS2` → `gmm_fits_D2_U28NR16B16e4`; 비용 ≈ 19 분 추가). 사다리가 실행 커밋 1 전에 닫혀 한 묶음이면 chkS2 는 없다 |
| **태그·실행 (명령 원문)** | 태그 `<T>s<s>` (s = 2, 3): `U28NR16B16e4s{2,3}`, `U28NR32B16e4s{2,3}`, `NR32B16e4s{2,3}`. 실행: tmux 안에서 `bash code/run_seedsnr16e4.sh [--resume]` (스크립트가 `~/t2_wtS/conf` 로 이동하고 `CUDA_VISIBLE_DEVICES=` 를 export). 태그마다 runner 호출 = `runner.py run --testbed D2 --ntrain 160000 --prior <UMi28\|S2> --cell <C6\|C9> [--worker-gb <G>] --stagec-ckpt /home/HTJ/t2/conf/ckpt/<stem>_best.pt --n 2560 --chunk 40 --snr <판정점 3> --arm <11 arm> --tag <T>s<s>`. 순서: chkS → U28NR16 s2, s3 → U28NR32 s2, s3 → NR32 s2, s3 (사다리가 열려 있는 D2 C9 a3 가 마지막). 한 번에 하나(CPU 등록 실행은 한 번에 하나 — WORK_QUEUE 원칙); 다른 `runner.py run` 이 있으면 시작하지 않는다. raw 는 `~/t2_wtS/conf/raw_<T>s<s>/` (git 미추적, SCALE16e4 선례) |
| **묶음** | **1 묶음** = 실행 커밋 1: `seedsnr_s5.txt` 에 준비된 5 시드의 `SEED` 줄; `NR32B16e4s3` 는 줄이 없어 PENDING(실행하지 않고 끝 줄에 표시). **2 묶음**: 1 묶음 `SEEDSNR_DONE` 뒤, 사다리가 닫히면 `seedsnr_s5.txt` 에 그 줄(`SEED NR32B16e4s3 d2sx_NR32_N160000_a3_fb<k> <sha16>` 또는 `SEED NR32B16e4s3 -`)과 §5 의 그 칸만 더한 커밋(= 실행 커밋 2) → `bash code/run_seedsnr16e4.sh --resume` (chkS2 포함; 끝난 raw 는 건너뛰고 뒤 단계만 결정적으로 다시 돈다). 실행 커밋 1 전에 사다리가 닫히면 한 묶음으로 끝낸다. raw 마다 `run\|git` 은 하나(1 또는 2)이고 두 커밋의 `conf/code`·`Demo` 는 같다(스크립트 전제; SEEDS16e4 선례: 태그마다 다른 실행 커밋, 코드 동일) |
| **메모리 가드 (C9)** | SCALE16e4 결정 5 그대로: C9 의 모든 runner 호출에 `--worker-gb G`, **G = `scale2_s5.txt` 의 `WGB` = 8.0** (jobs = min(cpu, 태스크, floor(0.8·MemAvailable/G)); SCALE16e4 는 같은 셀·fits·arm 으로 45 h 동안 G 인상·OOM 없이 jobs 99). UMi28 C6·chkS 는 가드 없음(전체 코어). RSS > 1.25·G 또는 OOM 이면 멈추고 사용자에게 알린 뒤 `SEEDSNR_WGB=<G′> bash code/run_seedsnr16e4.sh --resume` (G′ ≥ G, G 와 같은 규칙; `seedsnr_s5.txt`·HEAD 불변; 자원 문제라 재개에 승인은 필요 없다). 01_RULES §4 의 예외는 SCALE16e4 동결 줄에 이미 있고 그대로 쓴다. RSS 는 기록하지 않는다(위 실측이 근거; SCALE16e4 §6.1.5 와 같음) |
| **수용 검사** (하나라도 어긋나면 그 태그 무효 → 원인 기록 → 재실행은 사용자 승인; 재실행하면 새 태그가 그 시드의 유일한 값) | (a) **단독 호출** `eval_accept.py --ntrain 160000 --prior <p> --nr <Nr> --bstar kron --kron-K <K> --ll-val <ll> --points <C>:<판정점> --ref-raw raw_<T> --fits-dir results/gmm_fits_D2_<T>s<s> --grid "full:<FK> kron:<KR>" --tag <T>s<s>:best:<sha>:<C>` → `results/review_next/<T>s<s>_accept.txt`: 청크 {(40k, 40)} × 3 점, meta ntrain·bstar·kron_K·ll_val (\|Δ\| ≤ 1e-9), ckpt sha·role best, iters 16, **R5-genie 4 키가 a1 raw 와 비트 동일**, 격자 완전성(병합 파일 + K ≥ 1024 후보 3 개). (b) **`--ref-arms all` 게이트** → `<T>s<s>_refarms.txt`: 점마다 "arms differing" 이 정확히 `['M-ours-dscore-C-V1']`, shared 2560/2560, 빠진 키 없음(선례의 ⊆ {V0, V1, V4, V4b} 에서 돌리지 않는 V0·V4·V4b 를 뺀 것). (c) 시드 태그 표 B 의 판정점(앵커 b\*, 스크립트 정규식 — 블록이 정확히 하나일 때만) = a1 의 판정점. (d) C9: 청크 전부의 `meta\|jobs`·`meta\|worker_gb` 존재, worker_gb ≥ `WGB` (값 집합은 `ACCEPT (k)` 줄; SCALE16e4 (k)). (e) 회귀 검사 chkS(2 묶음은 chkS2) 비트 동일(실패 = 전체 ABORT). (f) raw 마다 깨끗한 커밋 하나 = 그 실행 커밋, `conf/code`·`Demo` 가 동결 커밋과 같고 SCALE16e4 실행 커밋 b4433d3c 대비 `code/run_seedsnr16e4.sh` 추가뿐(스크립트 전제), load_raw 경고 0 (analysis 로그). (g) ckpt: 시드 `_best.pt` sha = §5 (스크립트 전제), `_best.pt` epoch == last `.pt` best_epoch·sigma_tag·split_hash = a1 (§5, 수동), raw `meta\|stagec_ckpt_id` 의 `epoch=`·`best_epoch=` 가 §5 와 같음(§6, 수동), a1 `_best.pt` sha 불변(스크립트 전제). (h) 표 머리말 N_train 160000, UMi28 태그는 UMi28 배너(§6, 수동). 무효 태그는 집계에서 "판정 못함 (수용 실패)" 로 센다 |
| **시드 강건성 라벨** (SEEDS16e4 §1 의 규칙 그대로, SEEDS3 의 절대 범주 표현; 분모 3 = a1·a2·a3) | 셀마다 시드별 표 B `b* → V1` (§2): **(i) = V1 이 적게 실패 (POWERED, ≥ 2/3)**; **(ii)/(iii) = "다름"**; **(iv)/학습 실패/수용 실패 = "판정 못함"**. 집계: 셋 다 (i) → **"시드 강건 (3/3 (i))"**; (ii)/(iii) 가 하나라도 → **"시드 의존 (k/3 (i), m 다름)"**; 그 밖 → **"판정하지 못함 (k/3 (i), j 판정 못함)"**. k·m·j 는 a1 을 포함한 세 시드에서 센다; a1 은 SCALE16e4 §6.1.3 의 라벨((i)) 그대로. 셀·예산·prior 한정 문장이며 arm 주장이 아니다. a1 을 다른 시드로 바꾸지 않고 세 시드를 한 표에 싣는다; BLER 을 본 뒤 시드를 고르지 않는다; 동등성은 주장하지 않는다. **사다리 한정어 (라벨 문자열의 일부; 보고 전용 아님)**: 어느 셀의 시드가 §3d 시행 2·3 의 체크포인트이면 그 시드의 §2 라벨과 그 셀의 집계 라벨에 `; a<s> = §3d fb<k>` 를 붙인다 — 예: D2 C9 "시드 강건 (3/3 (i); a3 = §3d fb2)". 한정어 없는 "시드 강건 (3/3 (i))" 은 세 시드가 모두 시행 1 일 때만 쓴다(SEEDS16e4·SEEDS3 문자열과 같은 뜻을 유지). §6 표·EXPERIMENTS 행·RESULTS 인용은 모두 이 문자열을 그대로 쓴다. §6 에서 D2 C9 는 등록 라벨(사다리)과 선례 규칙 라벨을 같은 표의 두 열로 나란히 적는다 |
| **문장 조건** (여기서 고정; 라벨이 아니다) | **(S1) 셀 문장**: 셀 라벨이 "시드 강건 (3/3 (i))" 이면 SCALE16e4 §6.1.3 의 그 셀 표 B 문장에 "(확산 시드 3/3)" 을 **붙인다**; 라벨에 사다리 한정어가 있으면 `"(확산 시드 3/3; a<s> = §3d fb<k> 클리핑)"` 으로 붙인다. 아니면 그 문장과 그 셀을 쓰는 SCALE16e4 문장(UMi28 C6: S1·S2·"전부(13 개)"; UMi28 C9: UMi28 1차·S2·"전부(13 개)"; D2 C9: D2 1차·D2 S2)에 **"단일 시드 한정 (SEEDSNR16e4: <집계 라벨>)"** 캐비엇을 붙인다(선례 "3/3 이 아니면 단일 시드 한정"). **(S2) 1차 (T+) 의 C9 시드 교체 유지**, 데이터셋 d ∈ {D2, UMi28} 마다: C9 셀의 시드 s 가 라벨 대상(학습 성공·수용 통과)이면 dR_d(s) = R_C9(시드 s) − R_C2(a1 등록 raw) 를 SCALE16e4 1차와 같은 명령형 `frontier_ci.py --recovery "raw_<T>s<s>:C9:<판정점>" "<C2 raw>:C2:<판정점>" --level 0.95` (C2 raw: D2 `raw_B16e4k` −3/0/+3, UMi28 `raw_U28B16e4` +3/+6/+9; 비짝 부트스트랩 B 2000, seed 20260926, C9 가 spec 1; 출력에 90 %·95 % 줄이 함께 있다)으로 구해, **SCALE16e4 §6.1.1 에서 그 데이터셋이 판정된 수준(D2 95 %, UMi28 90 %)의 CI 하한 > 0 이면 "유지"**. 두 시드 모두 유지일 때만 `"SCALE16e4 1차 (T+) 는 C9 확산 시드 a2·a3 에서도 유지된다 (2/2[; a3 = §3d fb<k>])"` 를 쓰고 SCALE16e4 의 G_d·Q-K·Q-OP 한정어를 그대로 붙인다(이 등록은 그것들을 다시 계산하지 않는다). 아니면 "유지 k/2 (시드 s: 하한 ≤ 0 \| 판정 못함 (사유))" 로만 쓴다. **(S3) UMi28 S1 "증가" 의 C6 시드 교체 유지**: S1(s) = R_C6(시드 s) − R_C2(a1) (같은 명령형, C6 가 spec 1), 90 % 하한 > 0 → 유지; 2/2 일 때만 "UMi28 S1 증가는 C6 확산 시드 a2·a3 에서도 유지된다 (2/2)". 공통: C2 끝은 등록 a1 raw 로 고정한다(C2 의 시드 산포는 SEEDS16e4 의 몫 — 이 문장의 범위 밖). (S2)(S3) 은 "모두 성립" 형이라 보정 없이 쓴다(교집합 규칙); 등록 사이 보정 없음. 2차 S2 단계(C9 − C6)·D2 S2 는 셀 사이 시드 짝이 임의라 다루지 않는다. 같은 명령을 a1 의 3 점 부분집합에 돌리면 SCALE16e4 값이 그대로 나온다(작성자 확인 (2)) |
| 보고 전용 | 시드별 판정점 점별 실패 수(b\*·V1·genie; b\*·genie 는 a1 과 같은 값임을 확인), pooled a:b 와 부호검정 p, 점별 R 과 R_dp [90% paired] (`recovery_ci`), 첫 판정점 V1 BLER (95% Wilson), SNR@0.1 격차(3 점 표; D2 C9 은 censored), `frontier_ci` 의 gaps 줄(ΣF_V1 − ΣF_g, ΣF_b\* − ΣF_g)과 dR·S1 의 다른 수준 줄, 가드 발동률, 세 시드의 val loss·epoch, 시드 간 산포(max − min)의 R_dp·ΣF_V1, `meta\|jobs`, D2 C9 의 선례 규칙 병기. 계산하지 않음: GB′, 𝔅, last, PIL·ALD, R\*@0.05·Q-OP, Q-K, 판정점 밖 점 |
| 다중성 | 시드 태그 6 개의 표 B 는 각각 보고하고, 새로 만드는 라벨은 셀별 집계 3 개뿐이다. 문장 (S2)(S3) 은 교집합형. 등록 사이 보정 없음. p ≥ 0.05 는 판정하지 못함이지 차이 없음이 아니다 |
| **실행 위치·커밋** | scale worktree `~/t2_wtS/conf` (SCALE16e4 의 raw·fits·σ·code 가 여기 있다; main 에는 병합된 코드만), GPU 숨김. **동결 커밋 (scale)** = 이 문서 v2 + `code/run_seedsnr16e4.sh` + `conf/DECISIONS.md` 동결 줄 + 검토 원문. **동결 전 main → scale 병합 금지**: 스크립트가 `git diff --name-status b4433d3c HEAD -- code ../Demo` = `A conf/code/run_seedsnr16e4.sh` 한 줄을 요구한다(main 의 그림 스크립트 등이 들어오면 ABORT; 그때는 새 동결). **실행 커밋 1** = §5 + `results/scale/seedsnr_s5.txt` 만(`git diff <동결> <실행 1> -- code ../Demo` 빈 것; SCALE16e4 결정 7 선례). **실행 중 scale 커밋 금지**(`run()` 이 HEAD 를 검사해 ABORT); 이 문서·`DECISIONS.md` 는 실행 중 편집하지 않는다(청결 전제, `--resume` 도 같다). main 커밋은 이 실행과 무관하다(`runner._git_head` 는 worktree 의 `code`·`../Demo` 만 본다). 실행 커밋 2 는 1 묶음 `SEEDSNR_DONE` 뒤에만. 결과 파일(tables·accept·refarms·recovery·manifest·guard·seedsnr_dR)·§6·감사는 scale 에 커밋한 뒤 main 으로 병합(양쪽 DECISIONS·EXPERIMENTS 줄 시간순 보존 — SCALE16e4 선례) |
| **실행 스크립트** | `code/run_seedsnr16e4.sh` (`run_seeds3_eval.sh`·`run_seeds16e4.sh` 의 태그별 흐름 + `run_scale2.sh` 의 `run`·`acc`·`kchk`·`dp`). §5 값은 `results/scale/seedsnr_s5.txt` 에서 읽는다: `FREEZE <동결 커밋>`, `SEED <tag> <ckpt_stem> <best_sha16>` 또는 `SEED <tag> -` (주석은 자기 줄에만); a1 셀 값(b\*·kron_K·ll_val·격자·a1 `_best` sha)과 `WGB` 는 `results/scale/scale2_s5.txt`. **전제**(실패 = 순서·자원 문제로 ABORT, 고친 뒤 승인 없이 재개): flock 단일 실행, `git status --porcelain code ../Demo` 빈 것, 이 문서·`DECISIONS.md`·두 s5 파일 추적·청결, HEAD = `seedsnr_s5.txt` 의 마지막 커밋, FREEZE 가 HEAD 의 조상이고 `code`·`Demo` 가 같음, b4433d3c 대비 이 스크립트 추가뿐, `common.CELLS["C9"]` = (−12..+6), `WGB` > 0 이고 `SEEDSNR_WGB` ≥ WGB, 다른 `runner.py run` 없음, SEED 줄 중복·미지 태그 없음, a1 raw 448 파일·a1 `_best.pt` sha = `scale2_s5.txt`, 시드 `_best.pt` sha = `SEED` 줄, fits 링크(시드 태그·chkS) 대상 일치, 이 등록의 기존 raw 는 `--resume` 일 때만(부분 raw 는 청크 전부의 `run\|git` 이 HEAD 일 때만 이어 감). **흐름**: (0) chkS run → 수용(`--ref-arms all`) → 실패 시 ABORT. (1) 시드 태그마다: run → `runner.py analysis` → 판정점 대조(수용 (c)) → `run_manifest` → `guard_report` → `recovery_ci --snrs <판정점>` → 수용 (a)(+C9 (d)) → `--ref-arms all` 게이트 (b) → (a)(b)(c) 통과 시 `frontier_ci` dR/S1 (`results/review_next/seedsnr_dR_<T>s<s>.txt`, 머리말 줄에 git·시각). `SEED … -` 는 실행 없이 "학습 실패" 로, 줄 없음은 PENDING 으로 로그. 로그 `logs/run_seedsnr16e4.log` (CDT), runner 로그 `logs/run_D2_<tag>.log` 는 호출마다 머리말 줄을 붙여 이어 쓴다. 끝 줄 **`SEEDSNR_DONE ok=<n> fail=<n> pending=<tags> trainfail=<tags>`**. **앞 초안 대비 바꾼 곳**: UMi28 C6 에도 S1(s) 계산 추가(앞 초안은 C9 만), `frontier_ci --level 0.90` → `0.95` (90 %·95 % 줄을 함께 출력 — (S2) 가 D2 95 %를 읽는다), 머리말의 "REPORT-ONLY" 를 §1 문장 조건으로, 본 루프의 입력을 fd 3 으로(루프 안 명령이 stdin 을 먹지 못하게). **작성자 검사**: `bash -n` 통과; 플래그를 argparse 와 grep 대조(`runner.py` `--testbed --ntrain --prior --cell --worker-gb --stagec-ckpt --n --chunk --snr --arm --tag`, `analysis`; `eval_accept.py` `--ntrain --prior --nr --bstar --kron-K --ll-val --n --points --ref-raw --ref-arms --fits-dir --grid --tag`; `recovery_ci.py` `--raw --cell --snrs`; `frontier_ci.py` `--recovery --level`; `guard_report.py` `--raw --testbed`; `run_manifest.py` `--tag`) — 전부 있음; 보조 함수 단위 시험(scratch): `s2c`·`sd` 파싱, `dp` 가 3 점 부분집합 표에서 '0 3 6' / '-3 0 3' / '-9 -6 -3', `refok` 이 V1 만 다른 출력은 통과·b\* 포함/shared 2559/빠진 키는 실패, `kchk` 이 C9 last raw 는 OK·C6 chk raw 는 FAILED. 스크립트는 실행하지 않았다 |
| **비용 (추정, 작성자 산술)** | 출처: SCALE16e4 §6.1 runner 표(A 태그 7 점·11 arm: UMi28 C6 120.8 분 @192 워커, UMi28 C9 820.0 분 @99, D2 C9 661.9 분 @99). 3 점이면 × 3/7: **51.8 / 351.4 / 283.7 분** (last 태그 3 점 실측 44.2 / 325.1 / 266.7 분과 정합). 시드 두 개: **≈ 22.9 h** + chkS 묶음마다 ≈ 0.3 h + 뒤 단계 수 분 → **1 묶음 ≈ 18.5 h, 2 묶음 ≈ 5.0 h**. 비교: 7 점 전부 ≈ 53.4 h; {V1, b\*, genie} 3 점 ≈ 21.2 h (−7 %, 그러나 analysis 불가). C9 의 jobs 가 99 가 아니면 시간은 99/jobs 배. GPU: 없음(fb2·fb3 학습은 이미 GPU 0·1 에서 진행 중, 등록 밖 비용). RAM: C9 워커 ≤ G = 8.0 GB × jobs |
| 무결성 | 이번 BLER 로 점·arm·가중치·시행·문장 수준을 고르지 않는다. 판정점은 a1 의 앵커 b\*, 가중치는 `_best.pt` (val loss), 사다리 시행은 번호 규칙. a1 은 보고용 arm 그대로 |

## 2. 라벨 (시드마다; SEEDS16e4 §2 표 그대로, UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

| 표 B `b* → V1` (시드 s, 셀 c) | 기록 |
|---|---|
| (i) POWERED 이고 second arm fewer ≥ 2/3 | "c 의 시드 s 에서 V1 이 b\* 보다 적게 실패" |
| (ii) POWERED 이고 first arm fewer ≥ 2/3 | "c 의 시드 s 에서 b\* 가 V1 보다 적게 실패" |
| (iii) POWERED, 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" |
| (iv) UNDECIDED (판정점 < 3 이거나 불일치 쌍 ≥ 6 인 판정점이 2 개 미만) | "판정하지 못함 (검정력 미달)" — 격자 확장 없음 |
| (i)–(iv) 가 §3d 시행 2·3 의 체크포인트에서 나온 경우 | 같은 문자열 + `"; a<s> = §3d fb<k>"` |
| 학습 실패 (D2 C9 a3 가 fb3 까지 실패) / 수용 실패 | BLER 없음 / 무효; "학습 실패 (시드 s)" / "수용 실패 (시드 s)"; 집계에서 "판정 못함", 분모 3 그대로 |

- 시드 강건성 라벨(§1)은 이 표의 셀별 집계다. 어느 결과도 SCALE16e4 의 판정·§6 을 바꾸지 않는다; 바뀌는 것은 §1 (S1) 의 캐비엇 유무와 (S2)(S3) 문장의 성립 여부뿐이다.

## 3. 미리 적는 예측 (SCALE16e4 a1 결과·SEEDS16e4/SEEDS3 결과·a2·a3 val loss·fb2 학습 곡선 epoch 643 까지를 본 뒤의 약한 예측; 각 항목 적중/빗나감 이분, 범위는 닫힌 구간·3 자리 값)

**채점 규칙(미리 고정)**: 예측 4–8 은 라벨 대상 태그(학습 성공·수용 통과)에 대해서만 채점한다. 학습 실패·수용 실패 태그가 있으면 그 태그를 뺀 나머지로 적중/빗나감을 정하고 "(n/6 태그 채점)" 을 옆에 적는다; 어느 셀의 라벨 대상 태그가 하나도 없으면 그 셀의 항목은 "채점 불가 (사유)" 로 적고 적중·빗나감 합계에 넣지 않는다. 예측 1–3·10–12 는 그대로 이분 채점한다(학습 실패는 1–3·10·11 의 빗나감).

1. **UMi28 C6 a2·a3 표 B 모두 (i)** → "시드 강건 (3/3 (i))".
2. **UMi28 C9 a2·a3 표 B 모두 (i)** → "시드 강건 (3/3 (i))".
3. **D2 C9 a2·a3 표 B 모두 (i)** → "시드 강건 (3/3 (i))".
4. 첫 판정점 V1 BLER: 두 시드 모두 a1 의 95% Wilson CI 안 — UMi28 C6 +0 dB [0.130, 0.157].
5. 같은 예측, UMi28 C9 −3 dB [0.124, 0.150].
6. 같은 예측, D2 C9 −9 dB [0.077, 0.099].
7. R_dp: 라벨 대상 시드 태그 모두 90% CI 가 a1 의 CI 와 겹친다(교집합 비어 있지 않음, 경계 포함) — UMi28 C6 [0.253, 0.322], UMi28 C9 [0.402, 0.462], D2 C9 [0.790, 0.832].
8. 셀마다 라벨 대상 시드(a1 포함)의 R_dp 의 산포(max − min) ≤ 0.05.
9. (낮은 확신) D2 C9 a2 (best val 0.1022046, 세 시드 중 최대) 의 R_dp < a1 의 0.811.
10. (S2) D2 "유지 2/2", UMi28 "유지 2/2"; (S3) UMi28 S1 "유지 2/2".
11. 학습: D2 C9 a3 fb2 가 발산하지 않고 끝나 a3 = fb2 (fb3 미사용).
12. 수용: chkS 비트 동일; 여섯 태그 모두 비-V1 10 arm 이 a1 과 비트 동일, 판정점 a1 과 같음, ACCEPT OK.
13. 빗나갈 경로 (예측 아님, 기록): (a) 어느 시드가 (ii)/(iii) → "시드 의존", §1 (S1) 캐비엇, 재선택 없음; (b) 수용 실패 → 무효·원인 기록, 재실행은 사용자; (c) fb2·fb3 모두 실패 → "학습 실패 (시드 a3)", D2 C9 집계 "판정하지 못함 (k/3 (i), 1 판정 못함)" 이상 불가; (d) chkS 실패 → 전체 ABORT, 사용자; (e) OOM → G′ 재개.

## 4. 선행 작업과 실행 현황 (갱신한다)

### 4.1 학습 (CDT; `logs/gpu_sched.log` 줄 번호와 학습 로그 `logs/train_d2sx_<stem>.log` 의 `# done` 줄; 학습 로그 머리말의 KST 는 `date` 로 환산)

| 시드 | 투입 → 종료 (`gpu_sched.log`) | 결과 (`# done`) | 중단·재개 |
|---|---|---|---|
| UMi28 C6 a2 | GPU 2, 10-01 02:58 → 07:54 CDT (:58, :73) | 867 epoch, best @847 val 5.221701e-01, patience, aborted False | 없음 |
| UMi28 C6 a3 | GPU 0, 10-01 03:34 CDT (:60) → SIGINT (:67 06:24 done 줄, :68 06:25 "SIGINT … epoch 491, aborted=True = not an attempt") → 재개 GPU 5 06:34 → 07:37 CDT (:71, :72) | 첫 구간 "491 epochs, stopped_by=interrupted, aborted=True" (best @486); 재개 머리말 `# =====` 10-01 06:41:30 CDT; **635 epoch, best @615 val 5.224268e-01, patience** | 1 회 (epoch 1–490 완료 뒤, epoch 491 을 저장 RNG 로 다시 학습) |
| UMi28 C9 a2 | GPU 4, 10-01 00:52 → 03:43 CDT (:55, :61) | 466 epoch, best @446 val 3.914202e-01, patience | 없음 |
| UMi28 C9 a3 | GPU 5, 10-01 00:52 → 06:33 CDT (:56, :70) | 937 epoch, best @917 val 3.913749e-01, patience | 없음 |
| D2 C9 a2 | GPU 2, 10-01 00:52 → 02:57 CDT (:53, :57) | 338 epoch, best @318 val 1.022046e-01, patience | 없음 |
| D2 C9 a3 (원 시행) | GPU 3, 10-01 00:52 → 08:33 CDT (:54, :74) | **1240 epoch, stopped_by=diverged**, best @1235 val 9.599885e-02 (epoch 1239–1240 val 7.4e+01 / 3.1e+01) → §3d | — |
| D2 C9 a3 fb2 | GPU 0, 10-03 18:12 CDT (:90) | 진행 중 (초안 작성 시 epoch 643, val 9.413645e-02 — 판정량 아님) → **1513 epoch, best @1493 val 9.184844e-02, patience, aborted False** (`gpu_sched.log:92` done rc=0 10-04 01:56 CDT; §5 부록) | 없음 |
| D2 C9 a3 fb3 | GPU 1, 10-03 18:12 CDT (:91) | **열지 않음** (체크포인트·sha·BLER); fb2 성공 뒤 10-04 02:24 CDT SIGINT, 재큐 안 함 (`gpu_sched.log:93–94`; 학습 로그 tail 열람 공개는 §5 부록·§6.1.7) | — |

- **규칙**: 이후의 중단·재개는 이 표에 **추가만** 한다; 체크포인트를 지우고 처음부터 다시 학습하지 않는다(같은 시드의 재추첨 금지; 하면 그 시드는 "학습 실패" 로 세고 분모 3 유지 — SEEDS3 §4 규칙).

### 4.2 열린 항목 (주 세션·사용자)

1. **§3d 적용이 선례(SEEDS16e4·SEEDS3 의 "사다리 없음")와 다르다** — 연구 판단에 해당하므로 주 세션이 사용자 확인을 받거나 DECISIONS 에 근거를 남길 것(§1 학습 실패 행; 선례 규칙 병기는 이미 등록됨). → **주 세션 결정 (동결 시)**: §3d 적용 유지 — 근거는 같은 추세의 D2 C6 a1 이 같은 늦은 발산 뒤 fb2 체크포인트라는 점과 번호 규칙(검증 손실·BLER 무관); 라벨 문자열의 사다리 한정어(M1)와 선례 규칙 라벨 병기로 공개; 근거는 DECISIONS 동결 줄.
2. 사용자 지시 원문·시각(머리 목록 첫 줄)과 DECISIONS 동결 줄. → **완료** (동결 커밋).
3. 사다리가 실행 커밋 1 전에 닫히면 한 묶음, 아니면 두 묶음(§1 묶음 행).
4. 적대적 검토 → v2. → **완료** (ROUND 2 반드시 0; 원문 `prereg_reviews_seedsnr/`).

### 4.3 현황

| 항목 | 상태 |
|---|---|
| `code/run_seedsnr16e4.sh` | 작성·`bash -n` 통과·보조 함수 시험(§1 실행 스크립트 행); 미추적 → 동결 커밋에 넣는다 |
| fits 링크 8 개 (`gmm_fits_D2_<T>s{2,3}` 6 + `gmm_fits_D2_U28NR16B16e4chkS` + `gmm_fits_D2_U28NR16B16e4chkS2`) | [실행 커밋 1 전] 생성 — 상대 링크, git 미추적(선례), 스크립트가 대상 일치 검사 |
| `results/scale/seedsnr_s5.txt` | [실행 커밋 1] §5 와 함께 커밋 (초안 §5 끝) |
| 적대적 검토 → v2 → 동결 → §5·실행 커밋 1 → 1 묶음 → (사다리) 실행 커밋 2 → 2 묶음 → §6 전사 → Fable 기록 감사 → `docs/EXPERIMENTS.md` 행 | §5·실행 커밋 1 d59b4c6c (10-03 23:03 CDT) → 1 묶음 → 실행 커밋 2 b53a8529 (10-04 17:36 CDT) → 2 묶음 → §6.1 **완료** (10-04 23:09 CDT) → 감사 §6.2 → EXPERIMENTS 행·DECISIONS 줄 (결과 기록 커밋) |

## 5. 평가 전 고정 기록 (실행 커밋 전에 채우고 커밋한다; 표기: 값은 초안 작성 시 관측(2026-10-03 22:59 CDT (= 10-04 12:59 KST)) — §5 커밋 때 파일로 재확인, **TBD(규칙)** = 아직 없는 값과 그것을 정하는 규칙)

| 항목 | UMi28 C6 a2 | UMi28 C6 a3 | UMi28 C9 a2 | UMi28 C9 a3 | D2 C9 a2 | D2 C9 a3 |
|---|---|---|---|---|---|---|
| `_best.pt` sha256[:16] · epoch · best_epoch · role | **f956a85c82ed4fb3** · 847 · 847 · best | **9c38545ab009f307** · 615 · 615 · best | **c11bb951ff7be4d4** · 446 · 446 · best | **7f72480c42fcd6c9** · 917 · 917 · best | **0c887ee786ff9dfa** · 318 · 318 · best | **03a5d4b2acabde01** · 1493 · 1493 · best (`d2sx_NR32_N160000_a3_fb2_best.pt`, §3d 시행 2) |
| last `.pt` sha256[:16] · epoch · best_epoch · stopped_by (평가 안 함) | e26ed7c35c52b876 · 867 · 847 · patience | 0a4592e302a23c65 · 635 · 615 · patience | a63316777178b994 · 466 · 446 · patience | ac384d5f5d1f7ac7 · 937 · 917 · patience | 8d9c5f0c6643a609 · 338 · 318 · patience | 5c9318143f4d579e · 1513 · 1493 · patience (`d2sx_NR32_N160000_a3_fb2.pt`) |
| 검사: `_best.pt` epoch == last `best_epoch` | 847 = 847 ✓ | 615 = 615 ✓ | 446 = 446 ✓ | 917 = 917 ✓ | 318 = 318 ✓ | 1493 = 1493 ✓ |
| best val | 0.5221701264381409 | 0.5224268436431885 | 0.3914201557636261 | 0.3913748860359192 | 0.10220460593700409 | 0.09184844046831131 |
| sigma_tag · split_hash · grad_clip · lr (= a1? ) | U28NR16g · 83e08c3911e52fc3 · 0.0 · 0.002238046051591068 (a1 같음 ✓) | 같음 ✓ | U28NR32 · 01735b4ef4b87ff8 · 0.0 · 같음 (✓) | 같음 ✓ | NR32 · 3669354ecf3a9f00 · 0.0 · 같음 (✓) | NR32 · 3669354ecf3a9f00 · 1.0 · 0.002238046051591068 (fb2 = 클리핑 1.0·같은 lr ✓; σ 격자 [3.2813e-02, 1.7404e+00]·split 은 a1 과 같음 ✓) |
| 참조 raw · a1 `_best` sha (`scale2_s5.txt`) | raw_U28NR16B16e4 · 34136808b1e367ac | 〃 | raw_U28NR32B16e4 · 463da87aa8dbfb61 | 〃 | raw_NR32B16e4 · 3cf5d3eff96f0341 | 〃 |
| 판정점 (스크립트 상수) | 0,3,6 | 〃 | −3,0,3 | 〃 | −9,−6,−3 | 〃 |
| 쓴 사다리 시행 | — | — | — | — | — | **fb2** (발산 없이 `stopped_by=patience`; fb3 는 fb2 종료 뒤 SIGINT, 재큐 안 함, 체크포인트 미개봉 — 선택은 번호 규칙; fb3 로그 열람 공개는 아래) |

- 읽은 것: ckpt 메타 키(`torch.load`, CPU, 가중치 미사용)와 파일 sha256, 학습 로그 `# done` 줄, a1 학습 로그의 σ·split 줄. a1 의 σ 격자·split_hash: UMi28 C6 [3.2943e-02, 5.4696e-01] · 83e08c3911e52fc3, UMi28 C9 [3.2958e-02, 1.7232e+00] · 01735b4ef4b87ff8, D2 C9 [3.2813e-02, 1.7404e+00] · 3669354ecf3a9f00 (각 a1 학습 로그) — 시드 로그와 같다.
- **§5 커밋 (실행 커밋 1) 때 재확인 (2026-10-03 23:03 CDT, 주 세션)**: 5 시드 `_best.pt` sha256[:16] 을 파일로 다시 계산 — 표와 같음; fits 링크 8 개 생성(상대 링크, 미추적); `results/scale/seedsnr_s5.txt` 작성(FREEZE 전체 해시). D2 C9 a3 의 사다리(fb2·fb3)는 아직 학습 중 → 2 묶음.
- **실행 커밋 2 (§5 부록; 10-04 17:36 CDT, 주 세션)**: 1 묶음 `SEEDSNR_DONE` (10-04 17:34 CDT) 뒤, `runner.py run` 프로세스 없음 확인. `results/scale/seedsnr_s5.txt` 에 `SEED NR32B16e4s3 d2sx_NR32_N160000_a3_fb2 03a5d4b2acabde01` 추가 (sha256 를 파일로 재계산). D2 C9 a3 열 = 위 표 (ckpt 메타 `torch.load` CPU·가중치 미사용, 학습 로그 `# done        : 1513 epochs, stopped_by=patience, aborted=Fa…`). §3d 사다리: fb2 작업 `done rc=0` (10-04 01:56 CDT, `gpu_sched.log`) · `# done` stopped_by=patience, aborted=False → 번호 규칙대로 fb2 사용; fb3 는 10-04 02:24 CDT 에 SIGINT (`gpu_sched.log` 주 세션 줄), 재큐 안 함.
  - **공개 — 봉인된 fb3 학습 로그 열람 (시행 선택에는 영향 없음)**: §1 은 fb3 를 열지 않는다고 정했으나 다음 열람이 있었다 (시각은 세션 기록의 도구 호출 타임스탬프에서 뽑음). (1) 주 세션 30 분 브리핑이 `tail -1 logs/train_d2sx_NR32_N160000_a3_fb{2,3}.log` 로 fb3 의 마지막 학습 줄 (epoch·train/val loss·best) 을 출력했다 — fb2·fb3 시작 (10-03 18:12 CDT) 직후부터 14 회 — 동결 전 10 회 (10-03 18:23 CDT, 10-03 18:54 CDT, 10-03 19:24 CDT, 10-03 19:54 CDT, 10-03 20:24 CDT, 10-03 20:54 CDT, 10-03 21:24 CDT, 10-03 21:54 CDT, 10-03 22:24 CDT, 10-03 22:54 CDT; 이 문서 초안·검토 중이며 작성자·검토자 서브에이전트에게는 전달되지 않음), 동결 뒤 4 회 (10-03 23:23 CDT, 10-03 23:54 CDT, 10-04 00:24 CDT, 10-04 00:54 CDT); 그 뒤 브리핑은 fb2 만 읽었다. (2) N-스케일링 설계 서브에이전트 (워크플로 wf_60e52925-e35) 가 10-04 03:27 CDT 에 fb3 로그 끝 (epoch 1608–1610, val ≈ 0.0952, best 9.523244e-02 @1608, 중단) 을 읽었다 — fb2 사용 결정 (10-04 01:56 CDT) 과 SIGINT (10-04 02:24 CDT) 뒤. 선택 규칙이 번호 규칙 (fb2 가 발산하지 않으면 fb2) 이라 열람이 시행 선택을 바꿀 수 없고, fb3 체크포인트·sha·BLER 은 보지 않았다. §6 에도 같은 공개를 적는다.
- 동결 커밋 해시: cd85bef199b0190d372da4a12996f4796f93d765. 실행 커밋 1·2 해시: d59b4c6ca15004c75b90068eeaaf379f43e97fc4 · b53a8529c55d3c5f58ab480c986fd530cd60a0cd (raw `run|git` 으로 §6.1 에서 확인).

**`results/scale/seedsnr_s5.txt` 초안** (실행 커밋 1 에 넣는다; FREEZE 는 동결 커밋의 `git rev-parse` 전체 해시):

```
# SEEDSNR16e4 §5 values read by code/run_seedsnr16e4.sh; committed WITH §5 (= the run commit). Comments ONLY on their own lines.
# Written 2026-10-03 22:59 CDT (= 10-04 12:59 KST). sha16 = sha256sum ckpt/<stem>_best.pt (first 16 hex). a1 values / WGB: results/scale/scale2_s5.txt.
# NR32B16e4s3: §3d ladder (fb2 / fb3) open at run commit 1 -> no SEED line (PENDING); its line comes in run commit 2.
FREEZE <full hash of the freeze commit>
SEED U28NR16B16e4s2 d2sx_UMi28NR16_N160000_a2 f956a85c82ed4fb3
SEED U28NR16B16e4s3 d2sx_UMi28NR16_N160000_a3 9c38545ab009f307
SEED U28NR32B16e4s2 d2sx_UMi28NR32_N160000_a2 c11bb951ff7be4d4
SEED U28NR32B16e4s3 d2sx_UMi28NR32_N160000_a3 7f72480c42fcd6c9
SEED NR32B16e4s2 d2sx_NR32_N160000_a2 0c887ee786ff9dfa
```

**DECISIONS 동결 줄에 적을 것**: 이 문서 v2 동결(해시), 사용자 지시 원문, 설계 선택(판정점 3 점·11 arm·chkS·(S1)–(S3))이 작성자·주 세션 선택임, §3d 를 선례와 다르게 적용한 근거와 선례 규칙 병기, a2·a3 가 등록 전 학습됐고 BLER 이 없었음, U28NR16 a3 SIGINT·재개, 동결 전 main → scale 병합 금지.

## 6. 결과 (이 절은 추가만 한다)

### 6.1 결과 (기록 2026-10-04 23:09 CDT (= 10-05 13:09 KST), Opus 5.5 서브에이전트 — 전사만, 해석 없음; 원본 `logs/run_seedsnr16e4.log`·`logs/run_D2_<T>.log` (청크별 BLER 줄은 옮기지 않음)·`logs/analysis_<T>.log`, `results/tables_D2_<T>.txt`·`results/guard_D2_<T>.txt`, `results/review_next/<T>_accept.txt`·`<T>_refarms.txt`·`recovery_<T>.txt`·`seedsnr_dR_<T>.txt`·`run_manifest_<T>.json`, raw `raw_<T>/` (meta·run 키만), `results/scale/seedsnr_s5.txt`·`scale2_s5.txt`; a1 값은 §0 과 SCALE16e4 §6.1)

표기: `L:n` = `logs/run_seedsnr16e4.log` n 행. `tab_<T>` = `results/tables_D2_<T>.txt`, `acc_<T>` = `results/review_next/<T>_accept.txt`, `ref_<T>` = `results/review_next/<T>_refarms.txt`, `rec_<T>` = `results/review_next/recovery_<T>.txt`, `dR_<T>` = `results/review_next/seedsnr_dR_<T>.txt`, `run_<T>` = `logs/run_D2_<T>.log`; `:n` = 그 파일 n 행. 시각은 로그 원값 CDT (KST 는 `date` 로 환산). "기록자 산술" = 파일의 정수 실패 수에서 Python 으로 계산 (R_dp 여섯 자리, Wilson, 산포, 경과 시간); 재현: `prereg_audit_2026-10-04/seedsnr_recompute.out` (여섯 자리 R_dp·Wilson 네 자리·산포·경과 시간은 §3·§5·§7, `recovery_<T>`·`seedsnr_dR_<T>` 파일의 바이트 재현은 §6; 감사 §6.2).

**동결·실행 커밋**: 동결 cd85bef1 (커밋 10-03 22:59:56 CDT). **실행 커밋 1** = §5 커밋 **d59b4c6c** (d59b4c6ca15004c75b90068eeaaf379f43e97fc4, 10-03 23:03:15 CDT) — 동결 대비 바뀐 파일은 이 문서와 `results/scale/seedsnr_s5.txt` (추가) 2 개, `git diff cd85bef1 d59b4c6c -- code ../Demo` 0 바이트. **실행 커밋 2** = §5 부록 커밋 **b53a8529** (b53a8529c55d3c5f58ab480c986fd530cd60a0cd, 10-04 17:36:46 CDT) — d59b4c6c 대비 바뀐 파일은 이 문서와 `seedsnr_s5.txt` (`SEED NR32B16e4s3 d2sx_NR32_N160000_a3_fb2 03a5d4b2acabde01`, `seedsnr_s5.txt:11`) 2 개, code·Demo 0 바이트. `git diff --name-status b4433d3c b53a8529 -- code ../Demo` = `A conf/code/run_seedsnr16e4.sh` 한 줄 (수용 (f)). 이 기록 시점 scale HEAD = b53a8529 (실행 커밋 2 뒤 scale 커밋 0), `git status --porcelain code ../Demo` 0 줄. (§5 끝의 "실행 커밋 1·2 해시: TBD" 는 위 두 값이고, raw `run|git` 으로 확인 — 아래 raw 절.)

**실행 (`logs/run_seedsnr16e4.log`)**:
- **1 묶음** (실행 커밋 1): `L:1` 10-03 23:03 CDT `start (git d59b4c6c, freeze cd85bef199b0190d372da4a12996f4796f93d765, resume 0, chk U28NR16B16e4chkS, WGB 8.0 (run 8.0), CUDA_VISIBLE_DEVICES='')` → chkS run·수용 (`L:2–3`, 23:23) → U28NR16B16e4s2 (`L:4–15`) → U28NR16B16e4s3 (`L:16–27`) → U28NR32B16e4s2 (`L:28–39`) → U28NR32B16e4s3 (`L:40–51`) → NR32B16e4s2 (`L:52–63`) → `L:64` `NR32B16e4s3 PENDING: no SEED line yet (§3d ladder open) -> batch 2 (§5 addendum commit, --resume)` → `L:65` 10-04 17:34 CDT **`SEEDSNR_DONE ok=47 fail=0 pending= NR32B16e4s3 trainfail= none`**, `L:66` `SEEDSNR_EXIT=0`. 경과 18 h 31 min (`L:1` → `L:65`, `date` 계산). ok 47 = chkS 2 (run·accept) + 태그 5 × 9 단계 (run·analysis·판정점·run_manifest·guard_report·recovery_ci·accept·ref-arms·frontier).
- **2 묶음** (실행 커밋 2, `--resume`): `L:67` 10-04 17:36 CDT `start (git b53a8529, freeze cd85bef199b0190d372da4a12996f4796f93d765, resume 1, chk U28NR16B16e4chkS2, WGB 8.0 (run 8.0), CUDA_VISIBLE_DEVICES='')` → chkS2 run·수용 (`L:68–69`, 17:57) → 1 묶음 5 태그는 `run <T> skip: raw complete (192 files)` (`L:71, 83, 95, 107, 119`) 뒤 뒤 단계 8 개를 다시 돌았다 (`L:72–81, 84–93, 96–105, 108–117, 120–129`, 17:57–18:05 CDT; 스크립트 머리말 `run_seedsnr16e4.sh:22` "a complete raw is skipped (post-run steps are re-run, deterministic)") → NR32B16e4s3 (`L:130–141`; run 18:05 → 22:51) → `L:142` 10-04 22:53 CDT **`SEEDSNR_DONE ok=51 fail=0 pending= none trainfail= none`**. 경과 5 h 17 min (`L:67` → `L:142`). ok 51 = chkS2 2 + 건너뛴 5 태그 × 8 + NR32B16e4s3 9. (§1 비용 행 추정: 1 묶음 ≈ 18.5 h, 2 묶음 ≈ 5.0 h.)
- 두 묶음 모두 ABORT·`fail`·`SKIPPED` 줄 0, `SEEDSNR_WGB` 인상 없음 (`L:1`·`L:67` 의 `WGB 8.0 (run 8.0)`). runner 로그 8 개는 각각 머리말 `# run_seedsnr16e4 …` 1 줄 (2 묶음에서 건너뛴 5 태그는 runner 를 부르지 않아 머리말이 붙지 않았다), warn/error/traceback/exception 0 줄 (기록자 grep). analysis 로그 6 개의 `WARNING` (load_raw 경고 형식) 0 줄 (수용 (f)).

**runner 실행 (태그별; `run_<T>` 의 머리말 줄 · workers 줄 · 첫 `done` 줄의 청크 초 · 끝 줄 `finished in`)**

| 태그 | 묶음 | 셀 · 점 · n | 체크포인트 (`run_<T>:5`) | 워커 (줄) | 첫 `done` 청크 (줄) | 소요 (줄) | 시작 → run 완료 CDT |
|---|---|---|---|---|---|---|---|
| U28NR16B16e4chkS | 1 | UMi28 C6 · −3 · 40 (청크 0) | a1 `34136808b1e367ac` @642 | 1 (:7) | 1176 s (:8) | 19.6 min (:9) | 10-03 23:03 (`L:1`, `:1`) → 23:23 (`L:2`) |
| U28NR16B16e4s2 | 1 | UMi28 C6 · +0/+3/+6 · 2560 | a2 `f956a85c82ed4fb3` @847 | 192 (:7) | 2735 s (:8) | 50.1 min (:200) | 23:23 (`L:4`) → 10-04 00:13 (`L:5`) |
| U28NR16B16e4s3 | 1 | 〃 | a3 `9c38545ab009f307` @615 | 192 (:7) | 2726 s (:8) | 50.3 min (:200) | 00:14 (`L:16`) → 01:05 (`L:17`) |
| U28NR32B16e4s2 | 1 | UMi28 C9 · −3/+0/+3 · 2560 | a2 `c11bb951ff7be4d4` @446 | 99 (:7 "memory guard allows 99 workers -> jobs = 99") | 10242 s (:9) | 347.0 min (:201) | 01:06 (`L:28`) → 06:53 (`L:29`) |
| U28NR32B16e4s3 | 1 | 〃 | a3 `7f72480c42fcd6c9` @917 | 99 (:7) | 10120 s (:9) | 350.1 min (:201) | 06:55 (`L:40`) → 12:45 (`L:41`) |
| NR32B16e4s2 | 1 | D2 C9 · −9/−6/−3 · 2560 | a2 `0c887ee786ff9dfa` @318 | 98 (:7 "memory guard allows 98 workers -> jobs = 98") | 8093 s (:9) | 286.0 min (:201) | 12:47 (`L:52`) → 17:33 (`L:53`) |
| U28NR16B16e4chkS2 | 2 | UMi28 C6 · −3 · 40 (청크 0) | a1 `34136808b1e367ac` @642 | 1 (:7) | 1211 s (:8) | 20.2 min (:9) | 17:36 (`L:67`, `:1` resume=1) → 17:57 (`L:68`) |
| NR32B16e4s3 | 2 | D2 C9 · −9/−6/−3 · 2560 | a3 = §3d fb2 `03a5d4b2acabde01` @1493 | 98 (:7) | 8152 s (:9) | 286.3 min (:201) | 18:05 (`L:130`, `:1` resume=1) → 22:51 (`L:131`) |

(C9 의 `--worker-gb 8.0` 는 머리말 줄 `:1` 의 명령에 있다. 첫 `done` 청크 초는 그 줄에 찍힌 청크 하나의 소요. 태그 뒤 단계 끝 (`frontier dR`) 시각: `L:15` 00:14, `L:27` 01:06, `L:39` 06:55, `L:51` 12:47, `L:63` 17:34, `L:141` 22:53; 2 묶음 재실행분 `L:81` 17:58, `L:93` 18:00, `L:105` 18:02, `L:117` 18:03, `L:129` 18:05.)

**raw (기록자 확인, 단일 프로세스·GPU 숨김; `meta|*`·`run|*` 키만 읽음)**: 8 태그 · 1154 npz — 시드 태그 6 × 192 (= 3 점 × 64 청크, 점마다 skip 0..2520 전부) + chkS·chkS2 각 1 (−3 dB, skip 0).
- **`run|git`**: `raw_U28NR16B16e4chkS`·`raw_U28NR16B16e4s2`·`s3`·`raw_U28NR32B16e4s2`·`s3`·`raw_NR32B16e4s2` = {d59b4c6c} (실행 커밋 1); `raw_U28NR16B16e4chkS2`·`raw_NR32B16e4s3` = {b53a8529} (실행 커밋 2). 태그마다 값 하나, dirty 표시 없음 (수용 (f) "raw 마다 커밋 하나"). a1 raw 3 개 (`raw_U28NR16B16e4`·`raw_U28NR32B16e4`·`raw_NR32B16e4`, 각 448) = {b4433d3c}.
- **`meta|stagec_ckpt_id`** (수용 (g) 의 §6 수동 대조): U28NR16B16e4s2 `sha256[:16]=f956a85c82ed4fb3 epoch=847 best_epoch=847 role=best 16x4`, s3 `9c38545ab009f307 epoch=615 best_epoch=615 role=best 16x4`; U28NR32B16e4s2 `c11bb951ff7be4d4 epoch=446 best_epoch=446 role=best 32x4`, s3 `7f72480c42fcd6c9 epoch=917 best_epoch=917 role=best 32x4`; NR32B16e4s2 `0c887ee786ff9dfa epoch=318 best_epoch=318 role=best 32x4`, s3 `03a5d4b2acabde01 epoch=1493 best_epoch=1493 role=best 32x4` → `epoch=`·`best_epoch=` 가 §5 와 같다 (847·615·446·917·318·1493). chkS·chkS2 `34136808b1e367ac epoch=642 best_epoch=642 role=best 16x4` (= a1 A raw). 같은 값이 `tab_<T>:47` (`stagec_ckpt_id`) 과 `run_<T>:5` 에 있다.
- `meta|ntrain` 전부 160000.0, `meta|bstar` 전부 kron, `meta|kron_K`·`meta|ll_val|kron` = §1 (UMi28 C6 4096 · 56.5879534445348, UMi28 C9 4096 · 152.23176788511105, D2 C9 2048 · 242.7371088214899), `meta|em_sec` = a1 계열 (75912.80111646652 / 128781.03982377052 / 421169.2490725517), `run|n` 40, `run|iters` 16, `run|seed` 20260926.
- **`meta|jobs`·`meta|worker_gb`**: UMi28 C9 두 태그 {99}·{8.0}, D2 C9 두 태그 {98}·{8.0}; UMi28 C6 두 태그·chkS·chkS2 는 키 없음 (가드 미사용 — §1 메모리 가드 행).
- 체크포인트 sha256[:16] (이 기록에서 `/home/HTJ/t2/conf/ckpt/<stem>_best.pt` 를 다시 계산): 시드 6 개 = §5 (f956a85c82ed4fb3, 9c38545ab009f307, c11bb951ff7be4d4, 7f72480c42fcd6c9, 0c887ee786ff9dfa, 03a5d4b2acabde01), a1 3 개 = `scale2_s5.txt:14–16` (34136808b1e367ac, 463da87aa8dbfb61, 3cf5d3eff96f0341) — 수용 (g) "a1 `_best.pt` sha 불변".
- run_manifest (JSON 줄 `L:8, 20, 32, 44, 56` (1 묶음) · `L:74, 86, 98, 110, 122, 134` (2 묶음)): n_raw_files 192 (6/6), config_hash — U28NR16B16e4s2·s3 d2e7f64a6e1fb841, U28NR32B16e4s2·s3 be3c3e0d438468f4, NR32B16e4s2 a501d45987ffbb39, NR32B16e4s3 3b35f7b7006763c7 (두 묶음 줄이 같다); `git_commit` 은 1 묶음 줄 d59b4c6c, 2 묶음 줄과 현재 파일 b53a8529 (`run_params.git` 은 raw 값 — 1 묶음 5 태그 d59b4c6c, NR32B16e4s3 b53a8529).
- 가드 보고 (`results/guard_D2_<T>.txt:16`, 6 태그): "NO GUARD FIRINGS in this raw set." (`:18` 10 arm 발동 0, `:19` R5-genie 해당 없음).

**수용 (원문; 로그 줄 = 1 묶음 / 2 묶음)** — 전부 통과:

| 태그 | `acc_<T>` 원문 | 로그 | `ref_<T>` 원문 (`--ref-arms all`; 게이트 = 점마다 "arms differing" 이 `['M-ours-dscore-C-V1']` 뿐) | 로그 |
|---|---|---|---|---|
| U28NR16B16e4chkS (회귀 검사, 1 묶음; `--ref-arms all` vs `raw_U28NR16B16e4`, 11 arm) | `ACCEPT: OK -- U28NR16B16e4chkS` (:1) | `L:3` | — (이 수용 자체가 `--ref-arms all`) | — |
| U28NR16B16e4chkS2 (회귀 검사, 2 묶음) | `ACCEPT: OK -- U28NR16B16e4chkS2` (:1) | `L:69` | — | — |
| U28NR16B16e4s2 | `ACCEPT: OK -- U28NR16B16e4s2` (:1) | `L:13` / `L:79` | `ACCEPT: FAILED` (:1); `U28NR16B16e4s2 ('C6', 0)` · `('C6', 3)` · `('C6', 6)`: `replay vs raw_U28NR16B16e4 (all): shared 2560/2560, arms differing ['M-ours-dscore-C-V1']` (:2–4) | `L:14` / `L:80` `ref-arms all U28NR16B16e4s2 (gate: only V1 may differ): arms differing ['M-ours-dscore-C-V1']  rc=0` |
| U28NR16B16e4s3 | `ACCEPT: OK -- U28NR16B16e4s3` (:1) | `L:25` / `L:91` | `ACCEPT: FAILED` (:1); `('C6', 0 · 3 · 6)` 세 줄 모두 `shared 2560/2560, arms differing ['M-ours-dscore-C-V1']` vs `raw_U28NR16B16e4` (:2–4) | `L:26` / `L:92` rc=0 |
| U28NR32B16e4s2 | `ACCEPT: OK -- U28NR32B16e4s2` / `  (k) raw_U28NR32B16e4s2: meta\|worker_gb ['8.0']  meta\|jobs ['99']` / `ACCEPT (k): OK` (:1–3) | `L:37` / `L:103` | `ACCEPT: FAILED` (:1); `('C9', -3 · 0 · 3)` 세 줄 `shared 2560/2560, arms differing ['M-ours-dscore-C-V1']` vs `raw_U28NR32B16e4` (:2–4) | `L:38` / `L:104` rc=0 |
| U28NR32B16e4s3 | `ACCEPT: OK -- U28NR32B16e4s3` / `  (k) raw_U28NR32B16e4s3: meta\|worker_gb ['8.0']  meta\|jobs ['99']` / `ACCEPT (k): OK` (:1–3) | `L:49` / `L:115` | 같은 형식 3 줄 vs `raw_U28NR32B16e4` (:2–4) | `L:50` / `L:116` rc=0 |
| NR32B16e4s2 | `ACCEPT: OK -- NR32B16e4s2` / `  (k) raw_NR32B16e4s2: meta\|worker_gb ['8.0']  meta\|jobs ['98']` / `ACCEPT (k): OK` (:1–3) | `L:61` / `L:127` | `ACCEPT: FAILED` (:1); `('C9', -9 · -6 · -3)` 세 줄 `shared 2560/2560, arms differing ['M-ours-dscore-C-V1']` vs `raw_NR32B16e4` (:2–4) | `L:62` / `L:128` rc=0 |
| NR32B16e4s3 | `ACCEPT: OK -- NR32B16e4s3` / `  (k) raw_NR32B16e4s3: meta\|worker_gb ['8.0']  meta\|jobs ['98']` / `ACCEPT (k): OK` (:1–3) | `L:139` | 같은 형식 3 줄 vs `raw_NR32B16e4` (:2–4) | `L:140` rc=0 |

(`ref_<T>` 의 첫 줄 `ACCEPT: FAILED` 는 `eval_accept --ref-arms all` 이 어느 arm 이든 다르면 쓰는 형식이다; 게이트는 `run_seedsnr16e4.sh:134–139` 의 `refok` — 첫 줄이 OK 이거나, FAILED 이고 나머지 줄이 모두 "shared 2560/2560, arms differing ['M-ours-dscore-C-V1']" 형식일 때 통과. 6/6 통과. 점별 `max |diff|` 값은 옮기지 않는다. 지금 남은 `acc_`·`ref_` 파일은 1 묶음 5 태그도 2 묶음 재실행본이며, 1 묶음 로그 줄의 문자열과 같다.)

→ **수용 (a)–(h)**: (a) 6/6 `ACCEPT: OK` (청크 계획·meta·ckpt id·genie 4 키 a1 비트 동일·격자 완전성). (b) 6/6 — 18 점 모두 "arms differing" = `['M-ours-dscore-C-V1']`, shared 2560/2560, 빠진 키 줄 없음 → **비-V1 10 arm (b\*·genie 포함) 이 a1 A raw 와 비트 동일**. (c) 판정점 = a1 6/6 (§6.1.1). (d) C9 4 태그 `ACCEPT (k): OK`, worker_gb {8.0} ≥ WGB 8.0, jobs {99}·{98}. (e) chkS (`L:3`)·chkS2 (`L:69`) 비트 동일. (f) raw 마다 커밋 하나 (위 raw 절), 두 실행 커밋의 code·Demo = 동결, b4433d3c 대비 이 스크립트 추가뿐, load_raw 경고 0. (g) 시드 sha = §5 (스크립트 전제 + 이 기록 재계산), raw `epoch=`·`best_epoch=` = §5, a1 sha 불변. (h) 표 머리말: GMM arm 예산 줄 `N_train=160000` (`tab_<T>:29–31, 33–36, 41`; `:32` R3-bigamp 는 `N_train=0`, 적합 없음), UMi28 4 태그는 `# SECOND TESTBED, STANDARD-MODEL SIDE (prior UMi28) -- 3GPP TR 38.901 via Sionna 2.1 …` 배너 (`tab_<T>:51`), D2 C9 두 태그는 배너 없음 (`:48` `prior S2`). → **수용 실패 0, 학습 실패 0 (D2 C9 a3 는 §3d fb2 성공)** → 라벨 대상 태그 6/6.

#### 6.1.1 판정점 (앵커 b\*; 수용 (c))

| 셀 | a1 (SCALE16e4 §6.1, 스크립트 상수) | s2 (로그 1 묶음 / 2 묶음) | s3 (로그) | 표 B 블록 판정점 줄 |
|---|---|---|---|---|
| UMi28 C6 | 0 3 6 | `'0 3 6' == a1 '0 3 6' rc=0` `L:7` / `L:73` | `L:19` / `L:85` | `tab_U28NR16B16e4s{2,3}:261` `decision SNRs ['+0', '+3', '+6'] (anchor M-ours-bstar: …)` |
| UMi28 C9 | −3 0 3 | `'-3 0 3' == a1 '-3 0 3' rc=0` `L:31` / `L:97` | `L:43` / `L:109` | `tab_U28NR32B16e4s{2,3}:261` `['-3', '+0', '+3']` |
| D2 C9 | −9 −6 −3 | `'-9 -6 -3' == a1 '-9 -6 -3' rc=0` `L:55` / `L:121` | `L:133` | `tab_NR32B16e4s{2,3}:258` `['-9', '-6', '-3']` |

각 표에 b\* → V1 블록은 정확히 하나 (`dp` 정규식). 판정점의 b\*·genie 실패 수는 세 시드에서 같다 (UMi28 C6 b\* 455·257·112 · genie 119·38·13; UMi28 C9 509·304·145 · 88·30·9; D2 C9 849·231·81 · 48·18·4 — `rec_<T>:2–4` = a1 `rec_U28NR16B16e4:5–7`·`rec_U28NR32B16e4:5–7`·`rec_NR32B16e4:5–7`) — 비트 동일 조건과 일치.

#### 6.1.2 시드별 표 B `b* → V1` (§2) 와 R_dp [90% paired]

| 셀 · 시드 (태그) | 점별 a:b (부호검정 p) | pooled (p) | 가드 · 유의 | §2 라벨 (등록 문자열) | **R_dp** [90% paired] (ΣF b\* · V1 · genie) | 출처 |
|---|---|---|---|---|---|---|
| UMi28 C6 a1 (`U28NR16B16e4`, 인용) | +0 114:26 (2.4e-14) · +3 81:11 (2.5e-14) · +6 37:7 (5.3e-06) | 232:44 (5.1e-32) | POWERED, 3/3 | (i) (SCALE16e4 §6.1.3) | 0.287 [0.253, 0.322] (824 · 636 · 170) | SCALE16e4 `:570`; §0; `rec_U28NR16B16e4:8` |
| UMi28 C6 a2 (`U28NR16B16e4s2`) | 113:33 (1.9e-11) · 80:13 (6.2e-13) · 37:8 (1.5e-05) | 230:54 (5e-27) | POWERED (3 점, 3 점 ≥ 6 불일치), second arm fewer 3/3, first 0/3 | **(i) "UMi28 C6 의 시드 a2 에서 V1 이 b\* 보다 적게 실패"** | **0.269** [0.231, 0.305] (824 · 648 · 170) | `tab_…s2:260–264`, `rec_…s2:5` |
| UMi28 C6 a3 (`U28NR16B16e4s3`) | 115:28 (1e-13) · 81:11 (2.5e-14) · 42:8 (1.2e-06) | 238:47 (6.6e-32) | POWERED, 3/3, 0/3 | **(i) "UMi28 C6 의 시드 a3 에서 V1 이 b\* 보다 적게 실패"** | **0.292** [0.255, 0.328] (824 · 633 · 170) | `tab_…s3:260–264`, `rec_…s3:5` |
| UMi28 C9 a1 (`U28NR32B16e4`, 인용) | −3 173:13 (7.3e-37) · +0 136:12 (9e-28) · +3 82:7 (2.4e-17) | 391:32 (1.3e-79) | POWERED, 3/3 | (i) | 0.432 [0.402, 0.462] (958 · 599 · 127) | SCALE16e4 `:571`; `rec_U28NR32B16e4:8` |
| UMi28 C9 a2 (`U28NR32B16e4s2`) | 168:15 (6.6e-34) · 150:13 (1.1e-30) · 85:7 (3.8e-18) | 403:35 (2.1e-80) | POWERED, 3/3, 0/3 | **(i) "UMi28 C9 의 시드 a2 에서 V1 이 b\* 보다 적게 실패"** | **0.443** [0.412, 0.474] (958 · 590 · 127) | `tab_…s2:260–264`, `rec_…s2:5` |
| UMi28 C9 a3 (`U28NR32B16e4s3`) | 169:13 (8.8e-36) · 143:7 (4.3e-34) · 86:7 (2.1e-18) | 398:27 (9.1e-86) | POWERED, 3/3, 0/3 | **(i) "UMi28 C9 의 시드 a3 에서 V1 이 b\* 보다 적게 실패"** | **0.446** [0.416, 0.476] (958 · 587 · 127) | `tab_…s3:260–264`, `rec_…s3:5` |
| D2 C9 a1 (`NR32B16e4`, 인용) | −9 641:16 (1.6e-166) · −6 198:9 (1.6e-47) · −3 75:4 (5.2e-18) | 914:29 (3.7e-229) | POWERED, 3/3 | (i) | 0.811 [0.790, 0.832] (1161 · 276 · 70) | SCALE16e4 `:569`; `rec_NR32B16e4:8` |
| D2 C9 a2 (`NR32B16e4s2`) | 638:13 (1.2e-169) · 201:5 (5.9e-53) · 70:4 (1.3e-16) | 909:22 (1.6e-236) | POWERED, 3/3, 0/3 | **(i) "D2 C9 의 시드 a2 에서 V1 이 b\* 보다 적게 실패"** | **0.813** [0.790, 0.834] (1161 · 274 · 70) | `tab_…s2:257–261`, `rec_…s2:5` |
| D2 C9 a3 (`NR32B16e4s3`, §3d fb2) | 637:19 (1.4e-161) · 190:10 (2.9e-44) · 72:2 (2.9e-19) | 899:31 (1.8e-222) | POWERED, 3/3, 0/3 | **(i) "D2 C9 의 시드 a3 에서 V1 이 b\* 보다 적게 실패; a3 = §3d fb2"** | **0.796** [0.774, 0.816] (1161 · 293 · 70) | `tab_…s3:257–261`, `rec_…s3:5` |

(R_dp = `recovery_ci --snrs <판정점>` 의 `pooled 3 SNRs` 줄, paired bootstrap B 2000 seed 20260926, 90 % — §1 보고 전용 행의 등록 형식. 기록자 산술 여섯 자리: UMi28 C6 0.287462 / 0.269113 / 0.292049, UMi28 C9 0.432010 / 0.442840 / 0.446450, D2 C9 0.811182 / 0.813016 / 0.795600 (a1 / a2 / a3).)

#### 6.1.3 시드 강건성 라벨 (§1; 분모 3 = a1·a2·a3, a1 = SCALE16e4 §6.1.3 의 (i))

| 셀 | a1 · a2 · a3 | **등록 라벨** (§1 문자열 그대로) | 선례 규칙 라벨 (§1 학습 실패 행 병기, 보고 전용 — 라벨로 쓰지 않음) |
|---|---|---|---|
| UMi28 C6 (Nr 16) | (i) · (i) · (i) | **"시드 강건 (3/3 (i))"** | 같음 (사다리 미사용, 세 시드 모두 시행 1) |
| UMi28 C9 (Nr 32) | (i) · (i) · (i) | **"시드 강건 (3/3 (i))"** | 같음 (사다리 미사용) |
| D2 C9 (Nr 32) | (i) · (i) · (i; a3 = §3d fb2) | **"시드 강건 (3/3 (i); a3 = §3d fb2)"** | "판정하지 못함 (2/3 (i), 1 판정 못함)" — 선례 규칙이면 a3 = 학습 실패 (원 시행 `stopped_by=diverged`, §4.1) → "판정 못함"; a1·a2 (i) 만으로 정해지는 값 (§1) |

(셀·예산·prior 한정; arm 주장 아님; a1 은 그대로 보고용 시드이고 세 시드를 한 표에 싣는다 (위 §6.1.2); 동등성은 주장하지 않는다 — §1 라벨 행.)

#### 6.1.4 문장 조건 (§1 (S1)–(S3); 라벨 아님)

**(S1) 셀 문장** — 세 셀 모두 "시드 강건 (3/3 (i)…)" → SCALE16e4 §6.1.3 의 그 셀 표 B 문장 (`NEXT_EXPERIMENTS_SCALE16e4.md:569–571`) 에 붙인다; "단일 시드 한정" 캐비엇은 어느 셀에도 붙지 않는다:
- UMi28 C6: "UMi28 C6 (Nr 16) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)" **"(확산 시드 3/3)"**.
- UMi28 C9: "UMi28 C9 (Nr 32) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)" **"(확산 시드 3/3)"**.
- D2 C9 (사다리 한정어 있음): "D2 C9 (Nr 32) 에서 V1 이 b\* 보다 적게 실패 (배열 규모 축 측정, UNGATED)" **"(확산 시드 3/3; a3 = §3d fb2 클리핑)"**.

**(S2) 1차 (T+) 의 C9 시드 교체 유지** (dR_d(s) = R_C9(시드 s) − R_C2(a1 등록 raw); `frontier_ci.py --recovery "raw_<T>s<s>:C9:<판정점>" "<C2 raw>:C2:<판정점>" --level 0.95`, 비짝 B 2000 seed 20260926; 판정 수준 = SCALE16e4 §6.1.1 의 그 데이터셋 수준):

| 데이터셋 (수준) | 시드 | R1 = R_C9(시드) [90%] (b\* · V1 · genie) | R2 = R_C2 (a1) [90%] | **dR [판정 수준]** · p | 하한 > 0 | 출처 |
|---|---|---|---|---|---|---|
| D2 (95 %) | a2 | 0.813 [0.791, 0.835] (1161 · 274 · 70) | `raw_B16e4k` −3/0/+3 0.509 [0.470, 0.544] (864 · 488 · 125) | **+0.304 [95% +0.256, +0.357]** · 0.0000 | 예 → 유지 | `dR_NR32B16e4s2:3–4,6` |
| D2 (95 %) | a3 (§3d fb2) | 0.796 [0.774, 0.817] (1161 · 293 · 70) | 〃 | **+0.287 [95% +0.239, +0.341]** · 0.0000 | 예 → 유지 | `dR_NR32B16e4s3:3–4,6` |
| UMi28 (90 %) | a2 | 0.443 [0.413, 0.474] (958 · 590 · 127) | `raw_U28B16e4` +3/+6/+9 0.150 [0.108, 0.190] (800 · 712 · 215) | **+0.292 [90% +0.243, +0.344]** | 예 → 유지 | `dR_U28NR32B16e4s2:3–5` |
| UMi28 (90 %) | a3 | 0.446 [0.417, 0.477] (958 · 587 · 127) | 〃 | **+0.296 [90% +0.247, +0.347]** | 예 → 유지 | `dR_U28NR32B16e4s3:3–5` |

(undefined replicates 0, 네 파일 `:5`. R2 줄은 SCALE16e4 §6.1.1 의 R_C2 값 (D2 0.509 [0.470, 0.544], UMi28 0.150 [0.108, 0.190]) 과 같다.)
- **D2 — 유지 2/2** → "SCALE16e4 1차 (T+) 는 C9 확산 시드 a2·a3 에서도 유지된다 (2/2; a3 = §3d fb2)" + G_D2 + "[운영점 정합 강건]" "[K 상한 강건]" (G_D2 = SCALE16e4 §6.1.1 문자열 그대로, `NEXT_EXPERIMENTS_SCALE16e4.md:514`: "(b\* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 격자 끝·tol 정지 셀: D2 C9 `NR32B16e4` tol 정지 24/24 (b\* kron 2048 은 적합 격자 내부, 격자 끝 아님), D2 C2 `B16e4k` 격자 끝 kron 1024 (2048 미적합))"; Q-OP·Q-K 한정어 = SCALE16e4 `:542`). 이 등록은 G_d·Q-K·Q-OP 를 다시 계산하지 않았다.
- **UMi28 — 유지 2/2** → "SCALE16e4 1차 (T+) 는 C9 확산 시드 a2·a3 에서도 유지된다 (2/2)" + G_UMi28 + "[운영점 정합 강건]" "[K 상한 민감: 외삽 불가]" (G_UMi28 = `NEXT_EXPERIMENTS_SCALE16e4.md:515`: "(b\* = 등록 프로토콜의 GMM — kron K ≤ 4096, 재시작 3, EM 상한 500 반복·tol/patience 정지 — 이며 최적 GMM 이 아니다; 격자 끝·tol 정지 셀: UMi28 C9 `U28NR32B16e4` 격자 끝 kron 4096 (4096 멈춤)·tol 정지 24/24, UMi28 C2 `U28B16e4` 격자 끝 kron 4096 (4096 멈춤))"; 한정어 = SCALE16e4 `:543`).

**(S3) UMi28 S1 "증가" 의 C6 시드 교체 유지** (S1(s) = R_C6(시드 s) − R_C2(a1), 같은 명령형, 90 %):

| 시드 | R1 = R_C6(시드) [90%] (b\* · V1 · genie) | R2 | **S1(s) [90%]** · p | 하한 > 0 | 출처 |
|---|---|---|---|---|---|
| a2 | 0.269 [0.232, 0.305] (824 · 648 · 170) | `raw_U28B16e4` 0.150 [0.108, 0.190] | **+0.119 [90% +0.064, +0.175]** · 0.0000 | 예 → 유지 | `dR_U28NR16B16e4s2:3–6` |
| a3 | 0.292 [0.256, 0.327] (824 · 633 · 170) | 〃 | **+0.142 [90% +0.085, +0.197]** · 0.0000 | 예 → 유지 | `dR_U28NR16B16e4s3:3–6` |

→ **유지 2/2** → "UMi28 S1 증가는 C6 확산 시드 a2·a3 에서도 유지된다 (2/2)".
(공통: C2 끝은 등록 a1 raw 로 고정; (S2)(S3) 는 교집합형이라 보정 없음; 2차 S2 단계·D2 S2 는 다루지 않음 — §1.)

#### 6.1.5 보고 전용 (§1 보고 전용 행; 라벨에 쓰지 않음)

(a) **판정점 점별 실패 수 /2560 과 점별 R [90% paired]** (`rec_<T>:2–4`; b\*·genie 는 세 시드 같음 — §6.1.1):

| 셀 (점) | b\* | genie | V1 a1 · a2 · a3 | R a1 | R a2 | R a3 |
|---|---|---|---|---|---|---|
| UMi28 C6 (+0/+3/+6) | 455·257·112 | 119·38·13 | 367·187·82 · 375·190·83 · 368·187·78 | 0.262 [0.211, 0.310] · 0.320 [0.260, 0.378] · 0.303 [0.206, 0.396] | 0.238 [0.184, 0.288] · 0.306 [0.245, 0.366] · 0.293 [0.194, 0.384] | 0.259 [0.207, 0.307] · 0.320 [0.256, 0.379] · 0.343 [0.244, 0.438] |
| UMi28 C9 (−3/+0/+3) | 509·304·145 | 88·30·9 | 349·180·70 · 356·167·67 · 353·168·66 | 0.380 [0.339, 0.421] · 0.453 [0.398, 0.506] · 0.551 [0.479, 0.628] | 0.363 [0.321, 0.406] · 0.500 [0.443, 0.555] · 0.574 [0.500, 0.648] | 0.371 [0.329, 0.413] · 0.496 [0.444, 0.548] · 0.581 [0.504, 0.655] |
| D2 C9 (−9/−6/−3) | 849·231·81 | 48·18·4 | 224·42·10 · 224·35·15 · 231·51·11 | 0.780 [0.754, 0.806] · 0.887 [0.840, 0.930] · 0.922 [0.851, 0.986] | 0.780 [0.754, 0.806] · 0.920 [0.876, 0.961] · 0.857 [0.780, 0.921] | 0.772 [0.745, 0.798] · 0.845 [0.796, 0.890] · 0.909 [0.851, 0.961] |

(a1 열 출처 `rec_U28NR16B16e4:5–7`, `rec_U28NR32B16e4:5–7`, `rec_NR32B16e4:5–7`. pooled a:b 와 부호검정 p 는 §6.1.2.)

(b) **첫 판정점 V1 BLER@16 (95% Wilson; `tab_<T>` 표 A V1 줄)**: UMi28 C6 +0 dB — a1 0.143 (0.130, 0.157) 367 (§0), a2 **0.146 (0.133, 0.161)** 375 (`tab_U28NR16B16e4s2:74`), a3 **0.144 (0.131, 0.158)** 368 (`tab_U28NR16B16e4s3:74`); UMi28 C9 −3 dB — a1 0.136 (0.124, 0.150) 349, a2 **0.139 (0.126, 0.153)** 356 (`tab_U28NR32B16e4s2:74`), a3 **0.138 (0.125, 0.152)** 353 (`tab_U28NR32B16e4s3:74`); D2 C9 −9 dB — a1 0.087 (0.077, 0.099) 224, a2 **0.087 (0.077, 0.099)** 224 (`tab_NR32B16e4s2:71`), a3 **0.090 (0.080, 0.102)** 231 (`tab_NR32B16e4s3:71`). 첫 판정점 b\* / genie (세 시드 같음): 0.178 / 0.046, 0.199 / 0.034, 0.332 / 0.019 (`tab_<T>:73,76` · `:70,73`). (기록자 산술 Wilson 네 자리: a2·a3 = (0.1333, 0.1607)·(0.1307, 0.1579), (0.1262, 0.1530)·(0.1251, 0.1518), (0.0772, 0.0991)·(0.0797, 0.1020); a1 (0.1303, 0.1575), (0.1236, 0.1502), (0.0772, 0.0991).) D2 C9 a2 의 −9 dB V1 실패 수 224 는 a1 과 같은 수이고 짝 불일치는 다르다 (638:13 vs a1 641:16).

(c) **SNR@0.1 짝 격차 b\* − V1 [90%] (3 점 표; `tab_<T>` 표 B 블록 끝 줄)**: UMi28 C6 a2 +1.33 dB [+1.01, +1.56], a3 +1.41 dB [+1.09, +1.64] (`:265`; censored 0 %) (a1 3 점 부분집합 +1.41 [+1.09, +1.65], §0); UMi28 C9 a2 +2.39 dB [+2.08, +2.70], a3 +2.40 dB [+2.10, +2.70] (`:265`; 0 %) (a1 +2.29 [+1.99, +2.60]); D2 C9 a2·a3 `>= +2.76 dB (M-ours-dscore-C-V1 is already below 0.1 at the lowest grid SNR)` (`:262`; censored — §1 SNR 점 행 예고) (a1 "≥ +2.76").

(d) **frontier `gaps` 줄 (판정점 합, 블록 수, 90 %)과 dR·S1 의 다른 수준 줄**:
- gaps R1 (ΣF_V1 − ΣF_g / ΣF_b\* − ΣF_g): UMi28 C6 a2 478 [443, 514] / 654 [616, 696], a3 463 [430, 499] / 654 [616, 696] (`dR_U28NR16B16e4s{2,3}:7`); UMi28 C9 a2 463 [430, 495] / 831 [786, 871], a3 460 [426, 492] / 831 [786, 871] (`dR_U28NR32B16e4s{2,3}:7`); D2 C9 a2 204 [179, 228] / 1091 [1045, 1135], a3 223 [198, 248] / 1091 [1045, 1135] (`dR_NR32B16e4s{2,3}:7`). a1 (SCALE16e4 §6.1.4 (c)): UMi28 C6 466 [432, 501] / 654 [616, 696], UMi28 C9 472 [437, 505] / 831 [786, 871], D2 C9 206 [182, 231] / 1091 [1045, 1135]. gaps R2 (C2 a1): UMi28 497 [461, 532] / 585 [547, 623], D2 363 [332, 396] / 739 [697, 781] (`dR_<T>:8`, = SCALE16e4).
- 다른 수준 줄: D2 dR 90 % — a2 +0.304 [90% +0.264, +0.350], a3 +0.287 [90% +0.247, +0.332] (`dR_NR32B16e4s{2,3}:5`); UMi28 dR 95 % — a2 +0.292 [95% +0.233, +0.355], a3 +0.296 [95% +0.237, +0.358] (`dR_U28NR32B16e4s{2,3}:6`); UMi28 S1 95 % — a2 +0.119 [95% +0.053, +0.186], a3 +0.142 [95% +0.078, +0.207] (`dR_U28NR16B16e4s{2,3}:6`). 부트스트랩 p 전부 0.0000.

(e) **시드 간 산포 (a1·a2·a3, max − min; 기록자 산술)**: R_dp — UMi28 C6 0.023 (0.269–0.292; 0.022936), UMi28 C9 0.014 (0.432–0.446; 0.014440), D2 C9 0.017 (0.796–0.813; 0.017415). ΣF_V1 (판정점 합) — UMi28 C6 636 / 648 / 633 → 15, UMi28 C9 599 / 590 / 587 → 12, D2 C9 276 / 274 / 293 → 19.

(f) **세 시드의 best val loss · best epoch (판정량 아님; §0 `:30`, §5 `:129`)**: UMi28 C6 a1 0.5224766 @642 · a2 0.5221701 @847 · a3 0.5224268 @615; UMi28 C9 a1 0.3923236 @232 · a2 0.3914202 @446 · a3 0.3913749 @917; D2 C9 a1 0.0988171 @230 · a2 0.1022046 @318 · a3 (§3d fb2) 0.09184844046831131 @1493 (원 시행 @1235 0.0959989 는 평가 안 함).

(g) **가드 발동률**: 6 태그 모두 0 (`results/guard_D2_<T>.txt:16`). **`meta|jobs`**: UMi28 C9 99 (두 태그), D2 C9 98 (두 태그), UMi28 C6 키 없음 (192 워커, `run_<T>:7`). **D2 C9 선례 규칙 병기**: §6.1.3 표.

(h) **계산하지 않음 / n/a** (§1 SNR 점 행·보고 전용 행 그대로): V1 의 SNR@0.1 (D2 C9 격차는 censored), UMi28 C6 의 R(−3 dB), R\*@0.05·Q-OP, Q-K, 판정점 밖 V1 곡선, GB′, 𝔅, last, PIL·ALD.

#### 6.1.6 §3 예측 채점 (적중/빗나감 이분; §3 머리말 채점 규칙 — 예측 4–8 은 라벨 대상 태그만, 여기서는 6/6)

| # | 예측 (요지) | 결정하는 수 | 채점 |
|---|---|---|---|
| 1 | UMi28 C6 a2·a3 표 B 모두 (i) → "시드 강건 (3/3 (i))" | 230:54 (i), 238:47 (i); 등록 라벨 "시드 강건 (3/3 (i))" | **적중** |
| 2 | UMi28 C9 a2·a3 표 B 모두 (i) → "시드 강건 (3/3 (i))" | 403:35 (i), 398:27 (i); "시드 강건 (3/3 (i))" | **적중** |
| 3 | D2 C9 a2·a3 표 B 모두 (i) → "시드 강건 (3/3 (i))" | 표 B 909:22 (i), 899:31 (i; a3 = §3d fb2) — 굵은 글씨 조건은 성립; 등록 라벨 문자열은 "시드 강건 (3/3 (i); a3 = §3d fb2)" 이고, §1 (M1) 은 한정어 없는 "시드 강건 (3/3 (i))" 을 세 시드 모두 시행 1 일 때만 쓰게 한다 → 예측 문자열은 나오지 않았다 | **빗나감** (문자열 그대로 채점; §6.1.7 메모) |
| 4 | UMi28 C6 +0 dB V1 BLER 두 시드 ∈ [0.130, 0.157] | 0.146, 0.144 (6/6 태그 채점) | **적중** |
| 5 | UMi28 C9 −3 dB ∈ [0.124, 0.150] | 0.139, 0.138 | **적중** |
| 6 | D2 C9 −9 dB ∈ [0.077, 0.099] | 0.087 (224/2560 = 0.0875), 0.090 (231/2560 = 0.0902) | **적중** |
| 7 | R_dp 90% CI 가 a1 CI 와 겹침 (라벨 대상 시드 태그 모두) | UMi28 C6 [0.231, 0.305]·[0.255, 0.328] vs [0.253, 0.322]; UMi28 C9 [0.412, 0.474]·[0.416, 0.476] vs [0.402, 0.462]; D2 C9 [0.790, 0.834]·[0.774, 0.816] vs [0.790, 0.832] — 6/6 겹침 | **적중** |
| 8 | 셀마다 R_dp 산포 (a1 포함) ≤ 0.05 | 0.023, 0.014, 0.017 | **적중** |
| 9 | (낮은 확신) D2 C9 a2 R_dp < a1 0.811 | 0.813 (0.813016 vs 0.811182) | **빗나감** |
| 10 | (S2) D2 "유지 2/2", UMi28 "유지 2/2"; (S3) UMi28 S1 "유지 2/2" | D2 95% 하한 +0.256·+0.239; UMi28 90% 하한 +0.243·+0.247; S1 90% 하한 +0.064·+0.085 → 셋 다 2/2 | **적중** |
| 11 | D2 C9 a3 fb2 발산 없이 끝나 a3 = fb2 (fb3 미사용) | fb2 1513 epoch `stopped_by=patience`, aborted False; fb3 SIGINT·미사용 (§5 부록) | **적중** |
| 12 | chkS 비트 동일; 6 태그 비-V1 10 arm a1 과 비트 동일, 판정점 a1 과 같음, ACCEPT OK | chkS `L:3` OK (chkS2 `L:69` OK); ref-arms 6/6 V1 만; 판정점 6/6; ACCEPT OK 6/6 | **적중** |
| 13 | 빗나갈 경로 (기록) | (a) 미발동 ((ii)/(iii) 0); (b) 미발동 (수용 실패 0); (c) 미발동 (fb2 성공); (d) 미발동 (chkS·chkS2 OK); (e) 미발동 (OOM·G 인상 없음) | 예측 항목 아님 |

합계: 적중 10 (1, 2, 4, 5, 6, 7, 8, 10, 11, 12), 빗나감 2 (3, 9); 13 은 경로 기록.

#### 6.1.7 편차·캐비엇 (사실만)

- **두 묶음 구조**: 1 묶음 = 실행 커밋 1 d59b4c6c (`L:1–66`; chkS + 5 시드 태그, NR32B16e4s3 PENDING), 2 묶음 = 실행 커밋 2 b53a8529 (`L:67–142`, `--resume`; chkS2 + NR32B16e4s3). raw `run|git` 은 태그마다 하나 (1 묶음 6 raw d59b4c6c, 2 묶음 2 raw b53a8529); 두 커밋의 code·Demo 는 동결과 같다 (§1 묶음 행·SEEDS16e4 선례 그대로).
- **2 묶음의 뒤 단계 재실행 (스크립트 설계)**: `--resume` 이 완성된 1 묶음 5 raw 를 건너뛰고 (`L:71, 83, 95, 107, 119`) analysis·판정점 대조·run_manifest·guard_report·recovery_ci·accept·ref-arms·frontier 를 다시 돌렸다 (`L:72–129`). 그래서 지금 있는 그 5 태그의 결과 파일 (`tab_`·`guard_D2_`·`run_manifest_`·`rec_`·`acc_`·`ref_`·`dR_`) 은 2 묶음 재실행본이다: 머리말 git = b53a8529 (`tab_<T>:2`, `dR_<T>:1` "git b53a8529 2026-10-04 17:58–18:05 CDT", manifest `git_commit`), raw 는 d59b4c6c (`tab_<T>:49` `git=d59b4c6c`, manifest `run_params.git`). 1 묶음판 파일은 덮였다 (남아 있지 않아 바이트 대조 불가); 로그에 남은 두 묶음의 accept·ref-arms·판정점 문자열과 manifest config_hash 는 같다 (예: `L:13`=`L:79`, `L:14`=`L:80`, `L:8`·`L:74` d2e7f64a6e1fb841).
- **§3d 적용 (D2 C9 a3 = fb2)**: 등록 규칙 (§1 학습 실패 행; 선례 SEEDS16e4·SEEDS3 의 "사다리 없음" 과 다름). 시행 선택은 번호 규칙 (fb2 `stopped_by=patience` → fb2). 라벨 문자열에 사다리 한정어가 붙고 (§6.1.2·§6.1.3), 선례 규칙 라벨 "판정하지 못함 (2/3 (i), 1 판정 못함)" 을 보고 전용으로 병기했다. 원 시행 a3 `_best.pt` (@1235) 는 평가하지 않았다. fb3 체크포인트·sha·BLER 은 열지 않았다.
- **공개 (§5 부록 공개의 반복, 시각 그대로) — 봉인된 fb3 학습 로그 열람 (시행 선택에는 영향 없음)**: §1 은 fb3 를 열지 않는다고 정했으나 다음 열람이 있었다 (시각은 세션 기록의 도구 호출 타임스탬프에서 뽑음). (1) 주 세션 30 분 브리핑이 `tail -1 logs/train_d2sx_NR32_N160000_a3_fb{2,3}.log` 로 fb3 의 마지막 학습 줄 (epoch·train/val loss·best) 을 출력했다 — fb2·fb3 시작 (10-03 18:12 CDT) 직후부터 14 회 — 동결 전 10 회 (10-03 18:23 CDT, 10-03 18:54 CDT, 10-03 19:24 CDT, 10-03 19:54 CDT, 10-03 20:24 CDT, 10-03 20:54 CDT, 10-03 21:24 CDT, 10-03 21:54 CDT, 10-03 22:24 CDT, 10-03 22:54 CDT; 이 문서 초안·검토 중이며 작성자·검토자 서브에이전트에게는 전달되지 않음), 동결 뒤 4 회 (10-03 23:23 CDT, 10-03 23:54 CDT, 10-04 00:24 CDT, 10-04 00:54 CDT); 그 뒤 브리핑은 fb2 만 읽었다. (2) N-스케일링 설계 서브에이전트 (워크플로 wf_60e52925-e35) 가 10-04 03:27 CDT 에 fb3 로그 끝 (epoch 1608–1610, val ≈ 0.0952, best 9.523244e-02 @1608, 중단) 을 읽었다 — fb2 사용 결정 (10-04 01:56 CDT) 과 SIGINT (10-04 02:24 CDT) 뒤. 선택 규칙이 번호 규칙 (fb2 가 발산하지 않으면 fb2) 이라 열람이 시행 선택을 바꿀 수 없고, fb3 체크포인트·sha·BLER 은 보지 않았다. `logs/gpu_sched.log:94` (10-04 02:24 CDT) 의 "NOT opened (log/ckpt not read)" 는 이 공개보다 앞선 주 세션 메모이며, 위 브리핑 열람 14 회가 그 메모보다 먼저 있었다 — §5 부록 (10-04 17:36 CDT) 이 바로잡은 것이다. (이 기록자는 fb3 로그·체크포인트를 열지 않았다.)
- **D2 C9 jobs 98**: D2 C9 두 태그의 메모리 가드가 `jobs = 98` 을 냈다 (`run_NR32B16e4s{2,3}:7` "memory guard allows 98 workers -> jobs = 98 (min of cpu_count 192, tasks 192, floor(0.8 MemAvailable / G))"); a1 (SCALE16e4) 과 UMi28 C9 시드 태그는 99. G = 8.0 그대로, (k) OK, OOM·중단 줄 없음. RSS 는 기록하지 않았다 (§1 메모리 가드 행 "RSS 는 기록하지 않는다").
- **2 묶음 끝 `SEEDSNR_EXIT` 줄 없음**: 1 묶음은 `L:66` `SEEDSNR_EXIT=0` 이 있으나 이 문자열은 `code/run_seedsnr16e4.sh` 에 없다 (grep; 스크립트 밖 tmux 명령이 쓴 것); 2 묶음은 `L:142` 의 `SEEDSNR_DONE` 이 마지막 줄이다. 2 묶음 스크립트 종료 코드는 로그로 확인되지 않는다 (`SEEDSNR_DONE … fail=0`).
- **UMi28 태그 표 머리말의 V1 예산 줄** `N_train=28160000  rung=D2SXUMi28NR16160000 …` (`tab_U28NR{16,32}B16e4s{2,3}:38`) — a1 표 (`tab_U28NR16B16e4:38`, `tab_U28NR32B16e4:38`) 와 SEEDS16e4 (`tab_U28B16e4s2:38`) 에도 같은 표시가 있다; GMM arm 예산 줄 (`:29–31, 33–36, 41`; `:32` R3-bigamp 는 `N_train=0`, 적합 없음) 과 raw `meta|ntrain` 은 160000. D2 C9 태그는 `N_train=160000` (`tab_NR32B16e4s{2,3}:38`).
- **R_dp CI 두 출처**: 등록 R_dp 는 `recovery_ci` (paired, `rec_<T>:5`); `dR_<T>:3` 의 R1 CI 는 frontier 의 부트스트랩이라 셋째 자리가 다를 수 있다 (예: UMi28 C6 a2 [0.231, 0.305] vs [0.232, 0.305]; D2 C9 a2 [0.790, 0.834] vs [0.791, 0.835]) — SCALE16e4 §6.1.4 (a) 와 같은 사정.
- **config_hash**: NR32B16e4s2 a501d45987ffbb39 ≠ NR32B16e4s3 3b35f7b7006763c7 (두 raw 의 `run|git` 이 다름 — config_hash 는 `run|*` 값 집합을 담는다, SCALE16e4 §6.1.7); UMi28 의 s2·s3 는 같은 해시.
- **§0–§5 의 미갱신 칸** (편집 금지라 여기 적는다): §0 표 "a3 fb2 [학습 중]", §4.1 fb2·fb3 행 "진행 중", §4.3 마지막 행 "대기", §5 끝 "실행 커밋 1·2 해시: TBD". 값: 실행 커밋 1·2 = 위 커밋 절; fb2 = 1513 epoch, best @1493 val 0.09184844046831131, `stopped_by=patience`, aborted False, `gpu_sched.log` done rc=0 10-04 01:56 CDT; fb3 = 10-04 02:24 CDT SIGINT, 재큐 안 함 (§5 부록).
- **예측 3 메모**: 예측 3 의 문구는 v1 문구이고, 검토 반영 (머리 목록 둘째 줄) 은 §1 라벨 행·(S1)(S2)·§2 표 (M1) 와 §3 머리말 채점 규칙·예측 7·8 (M2) 을 바꿨으나 예측 3 은 바꾸지 않았다. 위 채점은 문자열 그대로이고, 굵은 글씨 조건 (a2·a3 표 B 모두 (i)) 만 읽으면 성립한다.
- 판정점 밖 점·V1 SNR@0.1·UMi28 C6 R(−3 dB) 은 측정되지 않음 (§1 SNR 점 행; §6.1.5 (h)). p 값은 서술용; 등록 사이 보정 없음 (§1 다중성 행).
- 커밋: 이 절·결과 파일·EXPERIMENTS 행·DECISIONS 줄은 주 세션이 scale 에 커밋한다; scale → main 병합은 main 의 NSCALE 실행이 끝난 뒤 (main conf/code 동결 구간). 다음 단계: Fable 기록 감사.

### 6.2 기록 감사 (수치 재계산 + 규칙·출처 감사, Fable 5.1 서브에이전트, 독립·읽기 전용; 2026-10-04 23:33 CDT (= 10-05 13:33 KST); `prereg_audit_2026-10-04/audit_SEEDSNR16e4.md` (`seedsnr_recompute.py/.out/.err`, `seedsnr_extra.py/.out`); raw npz·ckpt·로그·git 에서 독립 재계산 — analysis·recovery_ci·frontier_ci·eval_accept 미호출; 봉인 fb3 로그·체크포인트 미개봉)

수치·라벨·예측 채점 오류 **0** (540 + 99 검사, 불일치 0), 규칙 위반 **0** (§0–§6 조건 14 항목; 실행 절차 편차는 §6.1.7 공개 그대로). 다시 계산한 것: §0–§5 불변 (:1–157 = HEAD, hunk 1·삭제 0); 로그 142 줄 (ok 47·51 = rc=0 47·51, rc≠0 0, 경과 18 h 31 min·5 h 17 min)·runner 로그 8·manifest 6·수용 파일 14; raw 11 디렉터리 (청크 계획·`run|git` d59b4c6c 6/b53a8529 2/b4433d3c 3·meta·ckpt id·jobs/worker_gb·em_sec·**비-V1 10 arm 3 필드 a1 비트 동일 6/6**·chkS/chkS2 11 arm 비트 동일); 판정점 9 raw; 표 B 9 (a:b·p·pooled·POWERED·3/3 → (i)); R_dp 9 (`recovery_<T>` 바이트 재현)·dR/S1 6 (`seedsnr_dR_<T>` :3·:5·:6 바이트 재현·gaps); Wilson 9; 산포 6; 라벨 3 + 선례 병기 3; (S1)–(S3); 예측 12 (**3 은 문구 그대로 빗나감이 맞음** — 1·2 와 같은 구조, M1 이 한정어를 라벨 문자열에 포함; 굵은 조건 성립은 §6.1.6·§6.1.7 기록); fb3 공개 §5 ↔ §6.1.7 글자 동일 (끝 문장만 교체)·시각 18·선후·커밋 메시지 일치; EXPERIMENTS 행 8 칸·DECISIONS 줄. 위생 정정 3 건 (전부 선택; 수치·라벨·채점 불변) — 1–3 반영, 주 세션 결정 1 건 (4) 은 미반영 (감사 대상 본문 사본 `prereg_audit_2026-10-04/appended_61.txt` 는 반영 전 판):
1. [출처 정밀화] §6.1 수용 (h): "(`tab_<T>:29–36, 41`)" → "(`tab_<T>:29–31, 33–36, 41`; `:32` R3-bigamp 는 `N_train=0`, 적합 없음)" (`:32` 는 GMM arm 도 160000 도 아님, 6 표 전부). — 반영 (감사 문구 그대로). 같은 범위 표기 "(`:29–36, 41`)" 가 §6.1.7 의 UMi28 V1 예산 줄 항목에도 있어 (감사가 지목하지 않은 곳) 같은 문구로 고쳤다 (기록자 확장; 수치 불변).
2. [출처] §6.1 표기 문단: 기록자 산술의 재현 출처 `prereg_audit_2026-10-04/seedsnr_recompute.out` 추가 (기록자 스크립트는 스크래치라 소멸; SCALE16e4 감사 정정 3 선례). — 반영 (감사 문구 그대로).
3. [공개 보강] §6.1.7 fb3 공개 끝: `logs/gpu_sched.log:94` (10-04 02:24 CDT) 의 "NOT opened (log/ckpt not read)" 는 이 공개보다 앞선 주 세션 메모이고 브리핑 열람 14 회가 그보다 먼저였음을 한 문장 추가. — 반영 (감사 문구 그대로).
4. [주 세션 결정] §0–§5 의 미갱신 칸 4 곳 (:30 "a3 fb2 [학습 중]", :101–102 "진행 중", :120 "대기", :139 "TBD") 교체 문구 (값·라벨 불변; 원문은 감사 파일 "정정 필요" 4) — 기록자는 **미반영** (§0–§5 편집 금지); **주 세션이 결과 기록 커밋 때 감사 문구대로 반영** (SCALE16e4 정정 4 선례; :120 의 끝 구절만 "EXPERIMENTS 행 (추가됨, 미커밋)" → "EXPERIMENTS 행·DECISIONS 줄 (결과 기록 커밋)") (§0–§5 편집 금지 규칙; 주 세션 결정 사항이며 바꾸지 않아도 기록에 영향 없음; 값은 §6.1.7 "§0–§5 의 미갱신 칸" 항목).
EXPERIMENTS 행·DECISIONS 줄은 정정 없음. 메모: 예측 3 은 M1 뒤 어떤 결과에서도 적중 불가였던 등록 단계 미갱신 (전사 오류 아님); 산포 0.017415 는 반올림 전 차 (여섯 자리 값끼리의 차는 0.017416); 1 묶음 결과 파일은 덮여 바이트 대조 불가 (로그 50 쌍·config_hash 동일); fb3 열람 세션 타임스탬프는 파일로 검증 불가 (내부 정합성만); `SEEDSNR_EXIT` 는 tmux 줄; config_hash 정의 (`run_manifest.py:83–85`) 로 s2 ≠ s3 설명; D2 C9 jobs 98 의 MemAvailable 미기록; C2 끝 raw 는 `run|git` 없는 이전 형식.
