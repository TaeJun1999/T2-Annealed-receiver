# NEXT_EXPERIMENTS_SPARSE16e4 — 정적 6 데이터셋에서 V1 대 **모델 기반 희소 baseline** (SBL·OMP) (사전 등록 v2)

- 작성: 2026-09-29 19:09 CDT (= 09-30 09:09 KST) 초안 v1 (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 6·권고 9; `prereg_reviews_2026-09-29/review_SPARSE16e4.md`) → 검토 반영 코드 2381af57·62ed179e + 재튜닝 (v2a → v2b) → **v2 (기록 09-30 18:57 CDT, Opus 5.5)** → v2 재검토 (Fable 5.1 서브에이전트, 두 렌즈 × 2 회차; 원문 `prereg_reviews_2026-10-01/review_SPARSE16e4_v2.md`; 1 회차 stats-fair 반드시 0·integ 반드시 2, 2 회차 두 렌즈 반드시 1 씩 — 같은 항목; 아래 요약 표 뒤 두 줄) 반영 (1 회차 기록 09-30 18:57 CDT, 2 회차 기록 09-30 18:57 CDT); v1 원문 사본 `prereg_reviews_2026-09-29/SPARSE16e4_v1.md` → 동결 커밋 (= **sbl → main 병합 결과**, `DECISIONS.md` 같은 줄). 병합 해시는 만들기 전에 알 수 없으므로 `DECISIONS.md` 줄은 **sbl 팁 해시**를 적고, 병합(동결) 해시는 실행 로그 `start (git $H)`·`pairB_SP*.txt` 머리말·§6 첫 줄에 기록된다. 커밋 뒤 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_STATIC16e4.md` (정적 6 데이터셋, 같은 raw·시행, `pair_baselines --provenance manifest`), `NEXT_EXPERIMENTS_ALD16e4.md` (개발 튜닝 → 동결 → 테스트, 격자 끝 규칙, SNR 별 멈춤), `NEXT_EXPERIMENTS_SUPP16e4.md` §1 (표 B·라벨·X\*·R_X·문장 규칙).
- **작성 시점 공개**: 사용자 지시 2026-09-29 CDT ("빈 곳도 계획에 올려"; 빈 곳 2 = 무선 분야 리뷰어가 요구할 **희소 복원 baseline** 부재 — 09-27 요약 결정 대기 4번). 작성자는 정적 6 데이터셋의 기존 arm 결과(STATIC16e4 §6.1 포함)를 모두 봤고, 튜닝 세 판(v1_em·v2a·v2b)의 **개발 NMSE** (pick 과 ρ 별 점수) 를 봤다 (§5). 새 arm 3 개(SBL-loop, SBL-pilot, OMP-pilot)의 **BLER 은 한 번도 계산되지 않았다** — v1 스모크(`--sparse-arms`, D2 C2, 0 dB, 개발 시행 2560..2567, n = 8) 는 raw 구조·유한성만 확인했고 BLER 수치는 보지 않았으며 그 raw 는 삭제됐다; v2 스모크 (등록 명령과 같은 `--sparse-file`, 같은 개발 시행 n = 8, 7 SNR) 도 BLER 을 열지 않고 raw 를 지운다 (§4). ρ 32 확장(§5.3)은 −3 dB 를 5 데이터셋에서 계산했으나 결과를 저장하기 전에 중단돼 **NMSE 값이 기록·열람되지 않았다** (로그에는 "done" 줄만). D2 C6 튜닝은 진행 중이며 작성자가 본 것은 SNR 별 완료 줄뿐이다 (값은 끝나야 파일에 쓰인다).
- 목적: "학습된 prior 가 **데이터 없이 쓰는 표준 희소 모형**보다 나은가". SBL 은 블록마다 가상 채널(오버샘플 2-D DFT) 위의 희소 분산을 추정하는 Gaussian prior 로, b\* 와 **같은 EP 수신기** ('gmm_site', exact_prior) 에 들어간다 — 달라지는 것은 prior 뿐이다.

### v1 → v2 요약 (검토 반드시 6 + v2 작성 중 발견 + C6 규칙)
| 항목 | v2 에서 한 것 | 바뀐 절 |
|---|---|---|
| 반드시 1 — L·n_em 을 SNR 별로 | 규칙 `sparse_tune.per_snr_pick`: ρ 는 family(SBL/OMP) 마다 데이터셋당 하나 (SNR 별 최적의 SNR 평균 dB 최소), n_em·L 은 그 ρ 에서 **SNR 마다** 최소 NMSE. runner `--sparse-file <pick JSON>` 가 점마다 그 SNR 값을 쓰고 `meta|sparse` 에 기록 (2381af57) | §1 하이퍼파라미터·실행, §5 (데이터셋 × SNR 7 표) |
| 반드시 2 — EM 수렴 미달 | 검토의 (a) 채택: 갱신을 **MacKay 고정점** (Tipping 2001 식 16; `arms.SparsePrior(update="mackay")` 기본) 으로, n_em 격자 {1,2,3,5,10,25,50}; 격자 끝 규칙을 ALD16e4 와 같게 ("그 축을 한 단계씩 최대 2 회 확장"). 1 회째 (v2a → v2b: ρ 16, n_em 1·2·3) 완료, **2 회째 (ρ 32) 는 비용으로 중단** → 캐비엇 (§5.3). §0 둘째 줄·§3 다시 씀 | §0, §1, §3, §5 |
| 반드시 3 — `meta|sparse` 수용 검사 부재 | `run_sparse16e4.sh` 가 **모든 청크**의 `meta|sparse` = 그 SNR 의 pick 값인지 검사 (불일치 → 그 데이터셋 INVALID). 실행 전에는 pick sha256[:16] (C2 다섯 = §5 값) 과 "tune JSON 에 규칙을 다시 적용하면 pick 이 재현되는가" 를 검사 | §1 수용 |
| 반드시 4 — 비용·실행 조건 | 1 스레드 실측으로 CPU·h 재산정 (§1 비용). `--jobs` 는 두지 않는다 (runner 설계, 01_RULES §4: 전 코어) → **실행 중 다른 CPU 작업 없음** + 메모리 가드 (OMP 가 M × M 을 만든다). C6 의 ρ 는 비용이 아니라 같은 규칙이 정한다; ρ 8·16 두 경우의 비용을 적어 둔다 | §1 비용·실행 |
| 반드시 5 — 스모크 raw | `raw_spsmoke/`·`results/gmm_fits_D2_spsmoke` 삭제 확인 (워크트리·main 모두 부재) | §4 |
| 반드시 6 — 기존 출력 검사 | 데이터셋(행)마다 `pairB_SP<suf>.txt`·`SP<suf>_accept.txt` 가 있으면 그 행 ABORT (v1 스크립트의 `ls a* b*` 는 한쪽만 있으면 rc 2 로 통과하던 결함도 고침); 부분 raw 가 있으면 "resume" 로그 | §1 실행 |
| **v2 작성 중 발견** — 수용이 항상 실패 | v1 스크립트는 `eval_accept --tag SP<suf>:<ROLE>:<V1 sha>:<cell>` 를 넘겼으나 SP 실행은 `--stagec-ckpt` 를 쓰지 않아 `meta|stagec_ckpt_id` 가 없다 → 6 데이터셋 모두 "ckpt id … != sha" 로 수용 실패했을 것 (raw_B16e4k 로 재현). `eval_accept` 에 규격 `ROLE = SHA = '-'` (= Stage C arm 없음, 키가 **없어야** 통과) 추가, 스크립트는 `SP<suf>:-:-:<cell>`. 기본 경로 불변 확인 | §1 수용, §4 |
| C6 규칙 고정 | D2 C6 pick = **진행 중인 튜닝이 같은 규칙으로 쓰는 `results/sparse/pick_S2_C6.json`**. → **동결 전 종료 (09-30 18:53 CDT), §5.2 (가) 적용: pick `3958df589e385522`·tune `81dba7612d964a06` 고정, 동결 커밋 포함**. 실행 순서 C2 다섯 → NR16 (C6) 마지막; NR16 은 그 파일이 있을 때만 시작 (스크립트 게이트: 없으면 튜닝 종료를 기다려 복사, 튜닝이 산출 없이 끝나면 ABORT) | §1 실행, §5.2 |
| 권고 1–9 | 1 (OMPv) 미채택 → §2 에 plug-in 명시; 2 (γ 웜스타트) 미채택 → §2 에 평탄 재시작 명시; 3 → §2 "고정 L (SNR 별 튜닝)"; 4 → §2 on-grid 한정·NOMP 범위 밖; 5 → §1 주 라벨에 A1 문장, §3 정보 낮음 표기; 6 → 보고 전용 (정의 차이로 예측 아님); 7 → §4; 8 → §1 다중성 칸; 9 미채택 (arms.py 변경 필요 — 튜닝이 그 파일을 쓰는 동안 금지) | §1–§4 |
| 라벨·예측·판정 | v1 과 같다 (검토가 바꾸라고 한 것 없음). §3 은 v2b 튜닝을 본 뒤 다시 썼고 주장은 같다 | §1–§3 |

- **v2 재검토 1 회차 (기록 09-30 18:57 CDT; 원문 `prereg_reviews_2026-10-01/review_SPARSE16e4_v2.md` 의 "1회차" 절; stats-fair 반드시 0, integ 반드시 2 — 둘 다 반영; 라벨·예측·판정·pick 은 바뀌지 않는다; 1 회차 권고는 2 회차와 함께 반영, 다음 줄)**: **M1** — 등록 명령의 runner `--sparse-file` 경로 (2381af57: pick 적재 → `_sparse_at` → SNR 별 `meta|sparse`) 는 끝까지 실행된 적이 없고 §4 의 스모크 문장은 v1 (`--sparse-arms`) 그대로였다 → 동결 전 워크트리에서 **등록 명령과 같은 모양의 개발 시행 스모크** (D2 C2, 2560..2567, n = 8, 7 SNR, `--arm SBL-loop SBL-pilot OMP-pilot R5-genie`) + 스크립트의 `meta|sparse` 검사 블록 + `meta|stagec_ckpt_id` 부재 확인, BLER 미열람, 삭제 → §4 스모크 행·절차. 재검토 반영 시점에 수신기 없이 한 단일 프로세스 확인: 다섯 C2 pick 에 runner main 의 적재 → `_sparse_at` → `meta|sparse` 직렬화가 스크립트 검사의 기대값과 35 칸 모두 일치. **M2** — C6 pick 은 sha 로 고정되지 않고 규칙 재현 검사는 격자를 tune JSON 자신에게서 읽어, `run_sparse_ext.sh` (ρ 32 확장, 파일 제자리 덮어씀) 나 다른 `--n` 의 산출도 통과할 수 있었다 → 스크립트 규칙 재현 블록에 **tune JSON 의 n = 256 · 격자 = v2b assert** (실패 → 그 행 ABORT, 로그 문구 갱신). 확인: 다섯 C2 tune JSON 통과 (규칙 재현 True, sha = §5.1), ρ 32 를 더한 모의 tune·n 128 모의 tune 은 AssertionError rc 1 → §1 실행, §5.2
- **v2 재검토 2 회차 (기록 09-30 18:57 CDT; 같은 원문의 "2회차" 절; 두 렌즈 반드시 1 씩 — 같은 항목, 두 렌즈의 수정을 합쳐 반영; 라벨·판정·pick 은 바뀌지 않고, 예측 6 만 채점에서 뺀다)**: **M1** — 실행에 쓰는 C2 pick·tune 다섯 쌍 (`results/sparse/{pick,tune}_{S2,S2c,SV8e,UMi28,MIX3}_C2.json`), `results/sparse/v2b/` 사본, `logs/sparse_tune_*_C2.log`·`logs/sparse_ext*.log` 가 sbl 에서 **미추적**이었다. 병합(동결)은 커밋된 파일만 옮기므로 main 에서 C2 다섯 행이 모두 "pick file missing" ABORT 이고, 손으로 복사하면 raw 의 `run|git` (동결 커밋) 이 쓴 하이퍼파라미터를 담지 않는다 (ALD16e4 선례는 `results/ald/tune_PIL*.json` 추적) → **이 파일들은 동결 커밋에 들어간다** (main 세션이 병합 전에 sbl 에서 `git add`; §1 실행 전제, §4 커밋 대상, §5.1) + 스크립트가 sha 검사 바로 뒤에 **sha 가 고정된 행의 pick·tune JSON 이 둘 다 git 추적 + clean** 인지 검사 (아니면 그 행 ABORT). **권고 반영 (1·2 회차)**: C6 게이트는 파일이 아니라 튜닝 **프로세스 종료**를 기다린 뒤 복사 (쓰다 만 JSON 경쟁 없음); C6 규칙 재현은 runner 가 읽는 키 (ρ_SBL, ρ_OMP, SNR 별 n_em·L) 만 비교 + tune 의 prior·cell assert + pick·tune sha256[:16] 둘 다 로그, 결과별 처리와 "동결 전에 끝나면 sha 고정" 분기를 §5.2 에 미리 적음; 알 수 없는 행 인자 ABORT·`exit $FAIL`·run_manifest rc 로그; 새 arm 예외 시행 = 실패, arm 별 개수 로그·§6 (§1 수용); 비용·실행 행의 CPU 예외 (C6 튜닝 2 스레드) 와 SPARSE_DONE 전 sbl 워크트리·tmux `sparsetune` 보존; §2 에 SBL-loop n_em 문장 (루프 전용 튜닝 없음, 튜닝 표 기준 손해 한계) 과 고 SNR OMP-pilot = 파일럿 LS; §1 보고 전용에 SBL-loop NMSE@16 − SBL-pilot NMSE; §5.3 캐비엇 두 문장; 예측 6 → 보고 전용·채점 안 함 (`pair_baselines` 가 내지 않음); §1 새 arm 행의 "희소 prior 가 읽는 것" = cbar·eh2_prior; 메모리 가드 ABORT 의 허용 대응 (§1 비용); `sparse_tune.py` 정리 시점 (§4); 동결 해시 기록 위치 (머리말); 스모크 로그 미열람 (§4 절차). **미채택**: 1 회차 stats-fair "SBL 만 ρ 32 확장" (§5.3 캐비엇 두 문장으로 대신), 2 회차 stats-fair S3 "tune 로그 완료 줄 grep" (프로세스 종료 대기로 대신 — integ S1)

---

## 0. 알고 있는 것 (판정에 쓰지 않는다)
- 정적 6 데이터셋의 13 baseline 표 B 는 STATIC16e4 §6.1 (규칙 고정 사후 계산): D2 C2·D3·UMi28·MIX3 에서 V1 이 13 개 전부보다 적게 실패; C6 은 V1-pilot (iv), SV8e 는 b\*·b\*-scalar·gmm32·V1-pilot (iv).
- 튜닝 NMSE (§5, v2b; 파일럿 전용 사후평균, 개발 채널): SNR 평균으로 SBL 이 OMP 보다 1.0–1.7 dB 낮다 (C2 5 데이터셋). −3 dB 에서는 D2 C2 0.10 dB·D3 ≈ 0 dB 로 거의 같고, SV8e·UMi28·MIX3 는 1.0–1.5 dB. OMP 의 L 은 저 SNR 에서 3–8 (희소); SV8e·UMi28 ≥ +3 dB, MIX3 ≥ +6 dB, D2 C2 +15 dB 에서는 **L = 32 = N** (고른 N 개 atom 위의 LS 와 같다 — 그 SNR 에서는 LS 가 개발 NMSE 최소; 구조상 상한이며 격자 끝이 아니다). SBL 의 n_em 은 2–10 (MacKay 조기 멈춤이 정규화 손잡이).
- D2 의 경로 수 L ∈ {3..8} (off-grid 각도) — 희소 모형에 유리한 구조다. 38.901·SV8e 는 군집·확산 산란.

## 1. 고정되는 것
| 항목 | 값 |
|---|---|
| **새 arm (코드: 브랜치 sbl → 동결 커밋 = main 병합)** | `SBL-loop` = `arms.SparsePrior(Cs, Nr, Nt, ρ_SBL, n_em)` 를 `route_a(..., "gmm_site")` 에 (b\* 와 같은 수신기; 매 외부 반복마다 현재 (G, b) 로 γ 재추정); `SBL-pilot` = 같은 prior, `mode="pilot_only"` (파일럿만, 채널 믿음 고정); `OMP-pilot` = `arms.OMPSitePrior(Cs, Nr, Nt, ρ_OMP, L)` pilot-only, plug-in v = 1e-8 (ALD-pilot 과 같은 방식; 지지집합은 백색화 상관 최대, 계수는 GLS). Cs = 같은 데이터셋의 full K32 적합 표본 공분산 (R2 와 같은 초기 상태). 희소 arm 이 Cs 에서 읽는 것은 **cbar 와 eh2_prior 뿐** — Cs 의 대각 전력 (cbar = tr Cs / N: SparsePrior 의 평탄 초기값 cbar·N/M 과 수신기 초기 믿음 νE; eh2_prior = 송신 열별 평균 대각 전력: 수신기 초기 데이터 site 분산; `Demo/t2_route_a.py` 326–327); 단위 전력 채널이라 둘 다 ≈ 1. Cinv 는 exact_prior 경로에서 읽지 않는다 (같은 파일 336·374 행). 사전 A = `arms.dft_dict(Nr, Nt, ρ)` (M = ρ² N atom). **γ 갱신 = MacKay 고정점** γ_i ← \|μ_i\|² / (γ_i d_i), d_i = a_iᴴ K G a_i, K = (I + G A Γ Aᴴ)⁻¹ (N × N Woodbury 형; M × M 식과 상대 오차 ≤ 1e-13), **호출마다 평탄 초기값 cbar·N/M 에서 n_em 단계** (블록·외부 반복마다 재시작, 웜스타트 없음); prior site = CN(0, A diag(γ) Aᴴ + 1e-6 I) 의 정확한 Gaussian site |
| **하이퍼파라미터 (규칙; `code/sparse_tune.py`)** | 개발 채널 = 전용 스트림 `default_rng([20260930, TBID, PID, Nr, SNR+100])`, n = 256/SNR, 파일럿 site 는 수신기와 같은 `make_pilots` 파일럿, 점수 = 파일럿 전용 사후평균 NMSE (dB). 격자 ρ ∈ {1,2,4,8,16}, n_em ∈ {1,2,3,5,10,25,50}, L ∈ {1,2,3,4,6,8,12,16,24,32,48,64} (L ≤ N; L = N 은 LS 이므로 끝 아님). **선택 규칙 `per_snr_pick`**: family 마다 ρ = argmin_ρ mean_SNR[min_g NMSE(ρ, g, SNR)] (동률 → 작은 ρ); 그 ρ 에서 SNR 마다 g = argmin NMSE (동률 → 작은 g), g = n_em (SBL) / L (OMP). **격자 끝 규칙** (ALD16e4 와 같음): 고른 값이 격자 끝이면 그 축을 한 단계씩 **최대 2 회** 확장. 실제: 1 회째 완료 (v2a → v2b), 2 회째 (ρ 32) **중단** — §5.3 캐비엇, ρ 16 을 끝값으로 쓴다. 이 규칙은 **C6 에도 같다**: C6 은 v2b 격자 한 판으로 끝내고 끝값이면 끝값 + 같은 캐비엇 (더 확장하지 않는다) |
| **실행 (테스트 시행, 데이터셋마다)** | 위치 = **main (`~/t2/conf`), sbl → main 병합(= 동결 커밋) 뒤**. `bash code/run_sparse16e4.sh` (인자 없으면 6 행 전부, 표 순서): 행마다 `runner.py run --testbed D2 --prior <PR> --cell <CELL> --n 2560 --chunk 40 --ntrain 160000 --sparse-file results/sparse/pick_<PR>_<CELL>.json --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag SP<suf>` (fits 링크 `gmm_fits_D2_SP<suf>` → a1 적합; 스크립트 전역 `CUDA_VISIBLE_DEVICES=`, UMi28·MIX3 는 GPU 숨김 필수). **순서: D2 C2 → D3 → SV8e → UMi28 → MIX3 → NR16 (C6) 마지막**. **C6 게이트**: `results/sparse/pick_S2_C6.json` 이 main 에 없으면 스크립트가 sbl 워크트리의 튜닝 **프로세스** (`sparse_tune.py --prior S2 --cell C6`) 가 끝나기를 10 분 간격으로 기다린 뒤 (파일 출현이 아니라 프로세스 종료 — 쓰다 만 JSON 을 복사하지 않는다) `~/t2_wtSBL/conf/results/sparse/tune_S2_C6.json` 이 있으면 pick·tune 둘 다 복사하고 시작; 튜닝 프로세스가 산출 없이 사라지면 NR16 ABORT. 행마다 전제: 기존 출력 없음 (있으면 ABORT, 재실행은 사용자 승인), pick sha256[:16] = §5 (C2), **sha 가 고정된 행은 pick·tune JSON 이 둘 다 git 추적 + clean** (C2 다섯 쌍 `results/sparse/{pick,tune}_<PR>_C2.json` 과 `results/sparse/v2b/` 사본·튜닝 로그는 **동결 커밋에 포함** — 지금은 sbl 미추적, main 세션이 병합 전에 sbl 에서 `git add`; 스크립트가 sha 검사 바로 뒤에 검사, 아니면 그 행 ABORT), **tune JSON 의 prior·cell = 그 행**, **tune JSON 의 n = 256 · 격자 = v2b (ρ {1,2,4,8,16}, n_em {1,…,50}, L {1,…,64}; C6 포함 — ρ 32 확장·다른 n 의 산출은 ABORT)**, 규칙 재현 (runner 가 읽는 키만; §5.2), 메모리 가드 (아래 비용). **SPARSE BLER 이 도는 동안 (게이트 대기 포함, SPARSE_DONE 까지) main 커밋 금지** — raw 의 `run|git` 은 동결 커밋 하나여야 한다. 실행 중 다른 CPU 작업 없음 (**예외: sbl 워크트리의 S2 C6 튜닝 프로세스, 2 스레드 — 동결 전에 끝남; 그리고 2단계 GPU 적합·학습 (`~/t2_wtS`, `gpu_sched.sh` 가 띄우는 GPU 작업 6 개, 각 CPU 코어 1 개 + bash 루프 gpu_sched·edge_rule·batched_prefix 와 CPU 병합 `fit_gpu.py --merge`) — 동결 줄과 같은 내용, HISNR 기록 감사의 편차 공개 뒤 명시**). **SPARSE_DONE 전에는 `~/t2_wtSBL` 워크트리와 tmux `sparsetune` 을 지우지 않는다** (게이트가 거기서 읽는다). 중단되면 같은 명령(또는 행 접미사 인자, 예 `NR16`)으로 재개 — runner 가 끝난 청크를 건너뛴다 (잘린 npz 는 지우고 기록). 알 수 없는 행 접미사는 아무 행도 돌리지 않고 ABORT (ALD16e4 선례); 스크립트 종료 코드 = 실패 행 수 |
| **수용 검사** | `eval_accept.py --tag SP<suf>:-:-:<CELL>` (청크 {(40k,40)} × 7, meta ntrain·bstar·kron_K·ll_val = base 태그 값, iters 16, **`meta|stagec_ckpt_id` 없음** (Stage C arm 을 만들지 않는 실행), **R5-genie 4 키가 base raw 와 비트 동일**) **+ `meta|sparse` 가 모든 청크에서 그 SNR 의 pick 값** (`rho_sbl, rho_omp, n_em, L`; 스크립트 검사). 실패 → 그 데이터셋 무효 (라벨 없음, 원인 기록); 다른 데이터셋 라벨은 유지. **새 arm 의 예외 시행 = 실패** (01_RULES §4; `pair_baselines.fails` 가 blk_err 비유한 → 1 로 센다) — PIL/ALD arm 의 예외가 무결성 실패 (그 데이터셋 라벨 없음) 인 것과 다르다; arm 별 예외 시행 수는 스크립트가 로그에 찍고 (`[sparse] raised trials per new arm`) §6 에 옮긴다 (보고, 판정 불변) |
| **판정 (데이터셋마다)** | `pair_baselines.py --base raw_<TAG> --pil raw_PIL<suf> --ald raw_ALD<suf> --est PIL<suf> --extra raw_SP<suf> --add-baselines SBL-loop SBL-pilot OMP-pilot --cell <CELL> --prior <PR> --r0 at1 --provenance manifest --expect-bstar <§0> --expect …(STATIC16e4 §6.1 의 𝔅 12 라벨)` → 표 B `X → V1`, X ∈ {SBL-loop, SBL-pilot, OMP-pilot} (**새 라벨 18 개**); 나머지 13 은 STATIC16e4 인용 (`--expect` 로 기계 대조, 불일치 → 드리프트, rc 1). 라벨·X\*·R_X·가드는 SUPP16e4 §1 그대로 |
| **다중성** | 6 데이터셋 × 3 = **새 라벨 18 개**; b\* 6·𝔅 72 는 인용 (재계산·대조만). 보정 없음, 개수 문장만; 개별 (i) 을 독립 주장으로 쓰지 않는다; 보고 전용 pair 별도 |
| **주 라벨** | D2 C2: 새 3 개가 모두 (i) → **(A) "V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패"**; 그 밖 → (B) 개수 문장. 정보 있는 쌍은 A1 = `SBL-loop → V1` (루프 대 루프) 이고 파일럿 전용 두 쌍은 거의 예정이다 — (A) 는 A1 이 (i) 일 때만 가능하다 (논리는 "셋 모두 (i)" 와 같다). 나머지 5 데이터셋 = 측정 라벨 |
| **"전부" 문장 (16 개)** | 원 b\* (i) **이고** 등록 baseline 15 개(𝔅 12 + 새 3) 모두 (i) **이고** (ii) 0 **이고** R_{X\*} CI 하한 > 0 (X\* 는 새 arm 포함 16 개 중 −3 dB 실패 최소) → "데이터셋 d 에서 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다". C6·SV8e 는 STATIC16e4 의 (iv) 때문에 결과와 무관하게 불가능 |
| 보고 전용 | 새 arm 의 R_X·절대 격차·SNR@0.1 격차, −3 dB 실패 수, NMSE@16 중앙값, `b* → SBL-loop` 표 B (GMM 대 희소 모형; 등록 명령 `pair_baselines` 는 `x → V1` 쌍만 내므로 이 표는 결과 뒤 코드로만 계산된다 — 계산하면 그 사실을 적고 채점하지 않는다); **SBL-loop NMSE@16 − SBL-pilot NMSE** (SNR 별 dB = `pairB_SP<suf>.txt` 의 "report-only, median NMSE@16" 줄에서 두 arm 중앙값의 10·log10 비; raw 키 `<arm>|nmse` 는 시행 × 16 반복이고 `--add-baselines` arm 도 그 줄에 찍힌다; SBL-pilot 은 채널 믿음 고정이라 반복과 무관 — 루프의 데이터 열이 SBL 추정을 얼마나 바꾸는지, §2 의 n_em 문장과 함께 읽는다); 테스트 파일럿 전용 NMSE@1 (SBL-pilot·OMP-pilot, 10·log10 mean_trial nmse) 과 §5 개발 NMSE (10·log10 Σ‖e‖²/Σ‖h‖²) 의 SNR 별 차 — 정의가 달라 예측으로 채점하지 않는다 |
| **비용 (1 스레드 실측, 사설 스트림 채널; 수신기 EP 부분 제외)** | ep_site 1 회: C2 (N 32) SBL ρ 16 ≈ 0.0076 s/단계, ρ 8 ≈ 0.0014 s/단계; OMP ρ 16 ≈ 0.57 s (AᴴGA 가 M × M = 8192² 복소 → 최대 ≈ 1.15 GB/워커). C6 (N 64) SBL ρ 8 ≈ 0.013 s/단계, ρ 16 ≈ 0.042 s/단계; OMP ρ 8 ≈ 0.19 s (≈ 1.15 GB), **ρ 16 ≈ 3.2 s·≈ 4.35 GB/워커**. 희소 arm CPU 시간 = 2560 × Σ_SNR [(16 + 1)·n_em·t_단계 + t_OMP] 초 (SBL-loop 16 회 + SBL-pilot 1 회): D2 C2 ≈ 7.9, D3 ≈ 7.7, SV8e ≈ 5.2, UMi28 ≈ 3.3, MIX3 ≈ 5.5 (C2 합 ≈ 30 CPU·h; OMP 가 행마다 ≈ 2.8); C6 은 pick 에 따라 ≈ 9 (ρ 8·8, Σn_em ≈ 55) ~ ≈ 44 (ρ 16·16) ~ 최악 ≈ 190 (ρ 16, n_em 전부 50). 192 워커 (`--jobs` 없음, 01_RULES §4) 로 C2 행당 ≈ 10 분 안팎, C6 ≈ 15 분–1.5 h + 수신기 EP 부분. **메모리 가드** (스크립트): 필요 ≈ cpu_count × (16·M_OMP² B + 0.3 GB), M_OMP = ρ_OMP² N — C2 ρ 16 ≈ 264 GB, C6 ρ 16 ≈ 882 GB, C6 ρ 8 ≈ 109 GB; `MemAvailable` 이 모자라면 그 행 ABORT (사용자 결정; 규칙·pick 을 바꾸지 않는다). **허용 대응 (미리 적음)**: (a) 다른 작업이 끝나 `MemAvailable` 이 충분해지면 `bash code/run_sparse16e4.sh NR16` (또는 그 행 접미사) 재실행 — 규칙·pick 불변; (b) 코드 변경 (예: OMP 를 지지집합 위에서만 계산해 M × M 을 없앰) 은 **사용자 승인 + `DECISIONS.md` + 이미 끝난 C2 raw 의 OMP-pilot 키가 새 코드에서 비트 동일함을 확인한 뒤에만**; 그 밖의 대응은 없다 |

## 2. 라벨·문장
SUPP16e4 §2 그대로. 원고 문장 범위: 이 셀·예산·prior, **on-grid 오버샘플 2-D DFT 사전** (ρ 는 §5) 과 §1 튜닝 규칙의 SBL·OMP — SBL = MacKay 고정점 n_em 단계 (SNR 별 튜닝; 블록·외부 반복마다 평탄 초기값에서 재시작, 웜스타트 없음), OMP = **고정 L (SNR 별 튜닝)**, 잡음 기반 정지 없음, 채널 믿음은 **plug-in** (v = 1e-8, 오차 비인지). off-grid 방법 (NOMP 등) 은 범위 밖 (검토자 검사: Nr = 8 최악 on-grid 상관 ρ 4 0.975, ρ 8 0.994). ρ 16 은 격자 끝이며 확장 규칙이 끝나지 않았다 (§5.3) — 원고에 그렇게 적는다.
- **SBL-loop 의 n_em 은 파일럿 전용 개발 NMSE 로 SNR 별로 고른 값을 루프 안에서도 그대로 쓴다** (루프 가능도로는 튜닝하지 않았다 — 루프 전용 튜닝 없음). 루프에서는 데이터 열이 더해져 유효 SNR 이 높으므로 더 큰 n_em 이 나을 수 있다. 튜닝 표 기준 가능한 손해 (그 데이터셋 pick 의 −3 dB n_em 을 더 높은 SNR 에 쓸 때의 개발 NMSE 손해, SNR 중 최대): D2 C2 0.28 dB (+15 dB, n_em 5 대 10), **D3 0.85 dB** (+15 dB, 3 대 10), SV8e 0.15 dB (+12 dB), UMi28 0.05 dB, MIX3 0.09 dB — 대체로 ≈ 0.3 dB 이하이고, 방향은 SBL-loop 에 불리 = **V1 쪽으로 기운다**. 원고에 이 한계를 적는다 (§1 보고 전용의 "SBL-loop NMSE@16 − SBL-pilot NMSE" 와 함께).
- **새 arm 의 예외 시행 수가 0 이 아니면** 원고의 그 라벨 문장에 개수를 함께 적는다 (예: `(i), k raised trials counted as failures`) — 예외 시행은 실패로 세므로(§1 수용) V1 쪽으로 기우는 방향이다.
- **고 SNR 에서 L = N 이 골라진 점에서는 OMP-pilot 이 파일럿 LS 추정 (G⁻¹b; 독립인 N 개 atom 위의 GLS = LS) 과 같다**: SV8e·UMi28 ≥ +3 dB, MIX3 ≥ +6 dB, D2 C2 +15 dB (§0·§5.1; D3 는 없음, C6 은 pick 뒤 §6). 그 점의 OMP-pilot 결과를 원고에서 "희소 복원" 으로 부르지 않는다.

## 3. 미리 적는 예측 (v2b 튜닝 NMSE 와 기존 arm 결과를 본 뒤 다시 씀; 주장은 v1 과 같다; 새 arm BLER 은 미열람; 각 항목 적중/빗나감, 무효 데이터셋의 항목은 "판정 없음")
1. 주 라벨 D2 C2 = **(A)**.
2. D3·C6: 새 3 개 모두 (i) (데이터셋마다 한 항목; 파일럿 전용 두 쌍은 **정보 낮음**, SBL-loop 쌍이 정보).
3. UMi28·MIX3·SV8e: OMP-pilot → V1 은 셋 모두 (i) (한 항목; **정보 낮음** — 파일럿 전용 대 루프 V1).
4. UMi28·MIX3·SV8e: SBL-loop → V1 이 (i) 아닌 데이터셋 ≥ 1 (한 항목; 근거: 이 셋에서 V1 의 b\* 대비 우위가 작고 (R 0.06–0.14), SBL 이 개발 NMSE 에서 OMP 보다 1.0–1.7 dB 낮으며 −3 dB 에서도 1.0–1.5 dB 낮다 — 블록 적응 SBL 이 GMM 보다 나을 수 있다).
5. 새 18 라벨 중 (ii) ≤ 1 (한 항목).
6. 보고 전용 `b* → SBL-loop`: D2 C2 에서 b\* 가 SBL-loop 보다 적게 실패 (GMM 이 D2 분포를 학습). **보고 전용, 채점하지 않는다** (v2 재검토 2 회차): 등록 명령 `pair_baselines` 는 `x → V1` 쌍만 내고 X\* 도 V1 기준이라 이 쌍의 라벨을 내지 않는다 — 채점하려면 결과를 본 뒤 코드를 새로 써야 하고, 등록된 한 줄 채점 명령이 없다. 항목 번호는 유지하고 적중/빗나감을 매기지 않는다.
7. 빗나갈 경로: 수용·무결성 실패 → 그 데이터셋 무효; `--expect` 불일치 → 드리프트; C6 게이트·메모리 가드 ABORT → NR16 라벨 없음; pick·tune 미추적/dirty (sha 고정 행)·C6 규칙 재현의 ρ·n_em·L 불일치 → 그 행 ABORT (라벨 없음).

## 4. 선행 작업
| 항목 | 상태 |
|---|---|
| 코드 (브랜치 sbl): arms.dft_dict·SparsePrior (MacKay 기본, `update="em"` 선택)·OMPSitePrior + build_our_arms(sparse=…); runner `--sparse-arms`·`--sparse-file` (SNR 별; meta\|sparse 기록); pair_baselines `--add-baselines`; sparse_tune.py (`per_snr_pick`, `--rhos/--merge-with`) | 0c3607a6·9b27cfd4·1c5ffa6c·2381af57·62ed179e. 스모크 (v1, `--sparse-arms`): runner D2 C2 0 dB 개발 n = 8 — 세 arm raw 생성·유한·meta 기록 (`--sparse-file` 경로는 다음 행의 v2 스모크); Woodbury = M × M (1e-13); pair_baselines 기본 경로 = STATIC16e4 B16e4k 출력 비트 동일; `gamma_path` (튜닝 전용) = `gamma()` 비트 동일 (v2 작성 중 재확인: n_em 3·5·10, C2 ρ 8·16, C6 ρ 8). **`sparse_tune.py` 정리 완료 (동결 커밋)**: C6 튜닝이 동결 전에 끝나 (09-30 18:53 CDT) 동결 커밋에서 머리 docstring 의 규칙 문장을 v2 (`per_snr_pick`) 로 고치고 `main()` 의 죽은 루프 `for fam in ():` 를 지웠다 (동작 불변; 권고대로 정리 뒤 스크립트의 규칙 재현 블록을 여섯 pick 에 다시 돌려 rc 0 × 6, pick·tune sha 불변 확인) |
| 스모크 (v1: `--sparse-arms`, D2 C2 0 dB 개발 n = 8 — raw 삭제; **v2: 등록 명령과 같은 `--sparse-file` + `--arm SBL-loop SBL-pilot OMP-pilot R5-genie`, D2 C2 개발 시행 2560..2567 n = 8, 7 SNR**) | **v2 스모크 통과** (주 세션, 두 번): ① 09-30 18:33 CDT — runner rc 0, 청크 7, 오류 줄 0, 스크립트 검사 블록(그때 판) `0 mismatching chunks`, `meta|stagec_ckpt_id` 없음 True, 세 arm 키 True, NMSE 유한 True; ② 09-30 18:56 CDT — 검사 블록에 예외 시행 개수 출력이 더해진 뒤 같은 명령으로 다시: rc 0, 청크 7, 오류 줄 0, `raised trials per new arm … {'SBL-loop': 0, 'SBL-pilot': 0, 'OMP-pilot': 0}`, `0 mismatching chunks`, `meta|stagec_ckpt_id` 없음 True. 두 번 모두 BLER 미열람(로그 열지 않음), `raw_spsmoke2/`·fits 링크·로그 삭제, 잔여물 0 (`raw_spsmoke2`·`results/*spsmoke2*`·`logs/*spsmoke2*`, 워크트리·main). v1 스모크 raw (`raw_spsmoke/`, `results/gmm_fits_D2_spsmoke`) 도 부재 (삭제 시각 기록 없음) |
| v2 코드 (동결 커밋에 포함): `run_sparse16e4.sh` (`--sparse-file`, 행별 기존 출력 ABORT, resume 로그, pick sha·tune n·격자 = v2b (v2 재검토 M2)·규칙 재현·메모리 가드, C6 게이트, 행 선택 인자, eval_accept `-:-`); `eval_accept.py` (`ROLE = SHA = '-'` 규격; 기본 경로 불변 — raw_B16e4k 에 원 규격은 종전대로 실패, `-:-` 는 통과, 키가 있는 raw 에 `-:-` 는 실패 확인) | 작성 (`bash -n` 통과; runner·eval_accept·pair_baselines·run_manifest 인자 대조; C6 게이트 모의 시험 — 대기·복사·산출 없는 종료 ABORT; main 과 3-way 병합 충돌 없음; v2 재검토 뒤 규칙 재현 블록 단독 실행 — 다섯 C2 rc 0, ρ 32·n 128 모의 tune rc 1). **2 회차 반영**: sha 고정 행의 pick·tune git 추적 + clean 검사 (sha 검사 바로 뒤), C6 게이트 = 프로세스 종료 대기, 규칙 재현 = runner 키만 + tune prior·cell assert + pick·tune sha 로그, 알 수 없는 행 ABORT, run_manifest rc 로그, 새 arm 예외 시행 수 로그, `exit $FAIL` (행 표는 변수로 옮김 — 행 검사와 루프가 같은 표를 읽는다). 확인 (단일 프로세스, GPU 숨김, 수신기 없음): `bash -n`; 스크립트·문서 명령의 인자 전부 runner·eval_accept·pair_baselines·run_manifest argparse 에 있음; 모의 git 저장소 + 가짜 python 하네스 — 알 수 없는 행 (`NR17`, 빈 문자열) rc 1·start 전 ABORT, 추적·clean 쌍만 통과하고 tune 미추적·tune dirty·pick 미추적·둘 다 미추적은 각각 그 행 ABORT, PSHA `-` 행은 막히지 않음, 종료 코드 = 실패 행 수; 게이트 (가짜 프로세스 패턴·가짜 WT) — 산출 없음·pick 만 있음 → "pick file missing" ABORT, pick + tune → 복사; 규칙 재현 블록 — 다섯 C2 True (pick·tune sha = §5.1), 모의 pick 의 끝 플래그만 바꾸면 True, n_em·ρ_OMP 를 바꾸면 False rc 1, prior 불일치 AssertionError rc 1; `meta|sparse` 블록 — 가짜 raw 에서 예외 시행 수 집계·불일치 청크 rc 1; 앵커 pgrep 은 C6 튜닝 pid 276838 만 잡음 |
| 튜닝 6 데이터셋 | **6 완료** — C2 5 (v2b, §5.1); C6 09-30 18:53 CDT 동결 전 종료 → §5.2 (가) 적용 (sha 고정, 동결 커밋 포함) |
| 커밋 대상 — **동결 커밋 (sbl → main 병합에 포함; 지금 sbl 미추적 → main 세션이 병합 전에 sbl 에서 `git add`·커밋)**: `results/sparse/{pick,tune}_{S2,S2c,SV8e,UMi28,MIX3}_C2.json` (sha = §5.1 표; 스크립트가 main 에서 읽고 sha·git 추적 + clean 을 대조), `results/sparse/v2b/` (바이트 동일 사본, §5.1 근거), `logs/sparse_tune_{S2,S2c,SV8e,UMi28,MIX3}_C2.log`·`logs/sparse_ext.log`·`logs/sparse_ext_{S2,S2c,SV8e,UMi28,MIX3}.log` (§5.1·§5.3 근거), `prereg_reviews_2026-09-29/SPARSE16e4_v1.md`, `prereg_reviews_2026-10-01/review_SPARSE16e4_v2.md`, 이 문서, `run_sparse16e4.sh`·`eval_accept.py`; C6 튜닝이 동결 전에 끝나면 `results/sparse/{pick,tune}_S2_C6.json` + `logs/sparse_tune_S2_C6.log` 도 (§5.2); **명시 경로로만 `git add`** (`git add -A`·`.` 금지 — sbl 의 미추적 `conf/ckpt` 심볼릭 링크 제외). **동결 커밋 = 한 커밋**: main 에서 `git merge --no-commit sbl` 뒤 DECISIONS 동결 줄을 더해 커밋한 병합 커밋 (= 실행 로그 `start (git $H)` 의 HEAD) | 대기 (동결 전 `git add`) |
| 커밋 대상 — **실행 뒤** (선례와 같이): `raw_SP*`, `results/review_next/{SP*_accept.txt, pairB_SP*.txt, run_manifest_SP*.json}`, `logs/run_sparse16e4.log`·`logs/run_D2_SP*.log`; C6 튜닝이 동결 뒤에 끝나면 `results/sparse/{pick,tune}_S2_C6.json` (게이트가 복사) + `logs/sparse_tune_S2_C6.log` | 대기 |
| v2 → (재검토) → 동결 (sbl → main 병합) → 실행 (CPU; 앞선 SEEDS3 BLER·HISNR 은 끝남 — HISNR_DONE 09-30 17:09 CDT) | v2 + 재검토 반영 = 이 문서 (v2 스모크 실행 대기) |

**v2 스모크 절차 (동결 전, 워크트리 `~/t2_wtSBL/conf` — fits 있음; v2 재검토 M1)**. 7 태스크 = 7 워커 (runner 는 `min(cpu_count, 태스크 수)`), GPU 숨김. BLER 값은 열지 않는다 (tables·guard 파일은 열지 않고 지운다). **스모크 로그 `logs/run_D2_spsmoke2.log` 에는 개발 BLER 이 찍힌다** (runner 의 청크별 `done … BLER16:` 줄 — 목록에 있는 arm 은 R5-genie) — 로그는 열지 않고, 실패했을 때만 오류 줄 (`grep -nE 'Traceback|Error' logs/run_D2_spsmoke2.log`) 을 보며, 4 단계에서 raw 와 함께 지운다.
1. `ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_spsmoke2; CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python code/runner.py run --testbed D2 --prior S2 --cell C2 --n 8 --chunk 8 --skip0 2560 --ntrain 160000 --sparse-file results/sparse/pick_S2_C2.json --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag spsmoke2 > logs/run_D2_spsmoke2.log 2>&1`
2. `ls raw_spsmoke2/*.npz | wc -l` = 7 (검사 블록은 빈 폴더에서 0 불일치로 통과하므로 청크 수를 먼저 본다); 스크립트의 `meta|sparse` 검사 블록을 그대로: `sed -n '/^import sys, json, glob, re, numpy/,/mismatching chunks/p' code/run_sparse16e4.sh | ~/miniforge3/envs/torch/bin/python - raw_spsmoke2 results/sparse/pick_S2_C2.json` → "0 mismatching chunks", rc 0 (같은 블록이 찍는 `raised trials per new arm` 은 세 arm 모두 0 이어야 한다 — 0 이 아니면 동결하지 않고 원인을 찾는다).
3. `~/miniforge3/envs/torch/bin/python -c "import numpy as np,glob; print([('meta|stagec_ckpt_id' in np.load(f).files) for f in glob.glob('raw_spsmoke2/*.npz')])"` → 모두 False. 세 arm 의 존재·유한성 (값은 출력하지 않는다): `~/miniforge3/envs/torch/bin/python -c "import numpy as np,glob; zs=[np.load(f) for f in glob.glob('raw_spsmoke2/*.npz')]; print(all(k in z.files for z in zs for a in ('SBL-loop','SBL-pilot','OMP-pilot') for k in (a+'|nmse', a+'|blk_err')), all(np.isfinite(np.asarray(z[a+'|nmse'], float)).all() for z in zs for a in ('SBL-loop','SBL-pilot','OMP-pilot')))"` → True True.
4. `rm -r raw_spsmoke2 results/gmm_fits_D2_spsmoke2 logs/run_D2_spsmoke2.log results/tables_D2_spsmoke2.txt results/guard_D2_spsmoke2.txt` (있는 것만) → `ls -d ~/t2{,_wtSBL}/conf/raw_spsmoke* ~/t2{,_wtSBL}/conf/results/gmm_fits_D2_spsmoke*` 부재 확인 → 위 표 스모크 행의 상태 칸을 갱신.

## 5. 평가 전 고정 기록 (튜닝; 개발 NMSE 만)

### 5.1 C2 다섯 데이터셋 — 쓰는 pick = v2b
파일 `results/sparse/pick_<prior>_C2.json` (runner `--sparse-file` 입력) 과 근거 `tune_<prior>_C2.json`. 두 파일은 `results/sparse/v2b/` 사본과 바이트 동일하다. **다섯 쌍과 `v2b/` 사본·튜닝 로그는 동결 커밋에 들어간다** (지금 sbl 미추적; 스크립트가 main 의 파일을 읽어 sha 와 git 추적 + clean 을 행마다 대조하고, 아니면 그 행 ABORT). 셀 값 = 그 SNR 의 n_em (SBL) / L (OMP) (괄호 = 개발 NMSE dB). **끝** = 그 family 의 ρ 가 격자 끝 (JSON `edge_rho_*`); SNR 별 끝 플래그 (`edge_sbl`·`edge_omp`) 는 35 칸 × 2 모두 false (n_em 2–10 은 내부, L = N = 32 는 구조상 상한).

| SBL | ρ | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB | SNR 평균 |
|---|---|---|---|---|---|---|---|---|---|
| D2 C2 (S2) | 16 **끝** | 5 (−6.13) | 5 (−8.70) | 5 (−11.75) | 10 (−14.61) | 10 (−17.75) | 10 (−20.69) | 10 (−23.48) | −14.73 |
| D3 (S2c) | 16 **끝** | 3 (−6.57) | 5 (−9.31) | 5 (−12.19) | 10 (−14.36) | 10 (−17.77) | 10 (−21.01) | 10 (−23.52) | −14.96 |
| SV8e | 16 **끝** | 2 (−5.22) | 3 (−7.76) | 3 (−10.33) | 3 (−13.17) | 5 (−15.69) | 5 (−18.60) | 5 (−21.53) | −13.19 |
| UMi28 | 8 | 3 (−5.70) | 3 (−8.55) | 3 (−11.22) | 3 (−13.72) | 5 (−16.27) | 5 (−19.34) | 5 (−22.10) | −13.84 |
| MIX3 | 16 **끝** | 3 (−6.27) | 3 (−8.96) | 3 (−11.29) | 5 (−14.00) | 5 (−16.98) | 5 (−19.71) | 5 (−22.46) | −14.24 |

| OMP | ρ | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB | SNR 평균 |
|---|---|---|---|---|---|---|---|---|---|
| D2 C2 (S2) | 16 **끝** | 4 (−6.03) | 4 (−8.29) | 6 (−10.83) | 6 (−13.50) | 8 (−15.97) | 12 (−18.28) | 32 (−20.96) | −13.41 |
| D3 (S2c) | 16 **끝** | 3 (−6.57) | 4 (−9.10) | 4 (−11.42) | 6 (−13.33) | 8 (−16.13) | 8 (−19.02) | 12 (−20.98) | −13.79 |
| SV8e | 16 **끝** | 6 (−3.81) | 8 (−6.25) | 32 (−9.06) | 32 (−12.16) | 32 (−14.91) | 32 (−17.97) | 32 (−21.06) | −12.17 |
| UMi28 | 16 **끝** | 3 (−4.20) | 6 (−6.54) | 32 (−9.24) | 32 (−12.11) | 32 (−14.94) | 32 (−18.10) | 32 (−21.19) | −12.33 |
| MIX3 | 16 **끝** | 3 (−5.23) | 4 (−7.29) | 8 (−9.38) | 32 (−12.00) | 32 (−15.07) | 32 (−18.05) | 32 (−21.02) | −12.58 |

| 데이터셋 | pick sha256[:16] | tune sha256[:16] | 쓰인 시각 (파일 mtime) | 튜닝 벽시계 |
|---|---|---|---|---|
| D2 C2 (S2) | `2a6d79a23b6b6501` | `6f1e19bd6ce05bd3` | 09-30 00:16 CDT (= 14:16 KST) | 12444 s |
| D3 (S2c) | `afdb48498c76b88c` | `42b078018bea5471` | 09-30 00:03 CDT (= 14:03 KST) | 11656 s |
| SV8e | `72a6500e72950141` | `1b737191fdf8e668` | 09-30 00:21 CDT (= 14:21 KST) | 12745 s |
| UMi28 | `3d27f1bb72865fa5` | `4099975241c07a0d` | 09-30 00:07 CDT (= 14:07 KST) | 11872 s |
| MIX3 | `baffec3e463ad6b3` | `b02e6acacfb7aa5e` | 09-30 00:06 CDT (= 14:06 KST) | 11806 s |

- **출처·판 확인 (v2 작성 중)**: 여섯 튜닝 (C2 5 + C6) 은 `code/run_sparse_tune.sh` 한 번의 실행으로 09-29 20:49:14 CDT (= 09-30 10:49:14 KST) 에 함께 시작했다 (C6 프로세스 시작 시각 = 같은 초). 그때의 `sparse_tune.py` 는 2381af57 과 62ed179e 사이의 작업본이다 — tune JSON 격자 = v2b (ρ 1–16, n_em 1–50, L ≤ 64). 62ed179e 는 그 뒤 `--rhos/--merge-with` (ρ 32 확장용) 와 pick 의 `"rhos"` 키만 더했다: **62ed179e 의 `per_snr_pick` 을 다섯 tune JSON 에 다시 적용하면 pick 파일이 `"rhos"` 키를 빼고 정확히 재현된다** (끝 플래그 포함; 쓰인 pick 에는 `"rhos"` 키가 없다). `arms.py` 수정 시각 09-30 09:51 KST < 시작 → 2381af57 판 (MacKay), `common.py` 는 그 전부터 불변. runner 는 `rho_sbl, rho_omp, per_snr` 만 읽는다. 실행 스크립트가 같은 재현을 행마다 다시 검사한다.
- 앞선 판 (보관만, 쓰지 않음): `results/sparse/v1_em/` (EM 갱신, 격자 ρ ≤ 8·n_em 10–200·L ≤ 24, SNR 평균 한 값; 09-29 18:31–18:34 CDT; v1 §5 의 값), `results/sparse/v2a/` (MacKay, ρ ≤ 8·n_em 5–200·L ≤ 48, SNR 별; 09-29 20:08–20:09 CDT — 다섯 모두 ρ 8 (위 끝) 과 저 SNR n_em 5 (아래 끝) → 1 회째 확장 = v2b).

### 5.2 D2 C6 (S2, N = 64) — 규칙 고정, 값은 튜닝 산출
- **C6 pick = `results/sparse/pick_S2_C6.json`**, 진행 중인 튜닝 (`sparse_tune.py --prior S2 --cell C6 --n 256`, tmux sparsetune, `~/t2_wtSBL`, §5.1 과 같은 시작·같은 코드·같은 규칙·v2b 격자) 이 끝나며 쓰는 파일 그대로. 사람이 고르거나 바꾸지 않는다; 격자 끝이어도 확장하지 않는다 (끝값 + §5.3 캐비엇). (스크립트가 tune JSON 의 n·격자가 v2b 인지 검사한다)
- **튜닝 종료: 동결 전** — +15 dB 까지 끝나 09-30 18:53 CDT (= 10-01 08:53 KST, 79471 s) 에 pick·tune 을 썼다 (프로세스·tmux sparsetune 종료). 아래 (가) 를 적용했다: sha 를 이 절·스크립트 NR16 행 PSHA 에 적고 두 파일과 로그를 동결 커밋에 넣었다 (게이트는 건너뛴다).
| D2 C6 (S2, N = 64) | ρ | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB | SNR 평균 |
|---|---|---|---|---|---|---|---|---|---|
| SBL (n_em) | 16 **끝** | 3 (−6.88) | 5 (−9.76) | 5 (−12.78) | 5 (−15.62) | 5 (−18.57) | 10 (−21.59) | 10 (−24.52) | −15.68 |
| OMP (L) | 16 **끝** | 4 (−8.31) | 6 (−10.65) | 6 (−13.44) | 8 (−15.45) | 8 (−18.11) | 8 (−20.27) | 12 (−22.42) | −15.52 |

| 데이터셋 | pick sha256[:16] | tune sha256[:16] | 쓰인 시각 (파일 mtime) | 튜닝 벽시계 |
|---|---|---|---|---|
| D2 C6 (S2) | `3958df589e385522` | `81dba7612d964a06` | 09-30 18:53 CDT (= 10-01 08:53 KST) | 79471 s |

SNR 별 끝 플래그 전부 false (`edge_sbl`·`edge_omp`). 규칙 재현 검사 (스크립트 블록, 주 세션 09-30 18:58 CDT): rule-reproduced=True, 메모리 필요 ≈ 882 GB · 가용 1029 GB (그 시각).

- **도착 시점에 따른 처리 (미리 고정)**:
  - (가) **C6 튜닝이 동결 전에 끝나면**: main 세션이 pick·tune 의 sha256[:16] 을 이 절과 스크립트 NR16 행의 PSHA (`-` 자리) 에 적고, `results/sparse/{pick,tune}_S2_C6.json` + `logs/sparse_tune_S2_C6.log` 를 **동결 커밋에 넣는다** (sbl 에서 `git add`). 그러면 NR16 행도 C2 와 같이 sha·git 추적 + clean 검사를 받고 게이트는 건너뛴다 (sha 없이 도는 데이터셋이 없어진다).
  - (나) **동결 뒤에 끝나면**: 이 파일들은 동결 커밋에 없다. 스크립트가 튜닝 **프로세스 종료**를 기다려 (10 분 간격; 쓰다 만 JSON 을 복사하지 않는다) tune 이 있으면 pick·tune 을 main 으로 복사하고, 규칙 재현과 **pick·tune sha256[:16] 둘 다**를 로그에 남긴다; 값·두 sha 는 §6 에 옮기고 실행 뒤 결과와 함께 커밋한다.
- **규칙 재현 검사 (C6 에서 sha 대신 쓰는 고정)**: tune JSON 의 prior·cell = S2·C6, n = 256, 격자 = v2b 를 assert 하고, 동결 커밋의 `per_snr_pick` (규칙 본체는 2381af57·62ed179e 와 같다) 을 tune JSON 에 다시 적용해 **runner 가 읽는 키만** (ρ_SBL, ρ_OMP, SNR 별 n_em·L) pick 과 비교한다 — 끝 플래그·점수는 비교하지 않는다. 이유: 실행 중인 프로세스의 코드는 09-30 10:49:14 KST 작업본으로 git 에 없고, `edge_sbl` 의 하한 절 (`n_em == min(grid)`) 은 C2 산출에 n_em 1 이 없어 시험된 적이 없다. **결과별 처리 (미리 적음)**: 재현 결과가 끝 플래그에서만 다르면 구성상 통과한다 (비교 대상이 아니다; 끝 플래그는 §6 에 사실로 적는다); **ρ·n_em·L 이 하나라도 다르면 NR16 ABORT (라벨 없음)** — pick 을 손으로 고치거나 다시 튜닝하지 않는다.

### 5.3 캐비엇 — ρ 16 은 격자 끝 (확장 규칙 미완료)
- v2b 에서 ρ 가 끝값 16 인 것: SBL 은 D2 C2·D3·SV8e·MIX3 (UMi28 은 ρ 8 내부), OMP 는 다섯 모두. 규칙상 2 회째 확장 ρ 32 (`code/run_sparse_ext.sh`, `sparse_tune --rhos 32 --merge-with`) 를 09-30 00:23 CDT 에 다섯 데이터셋에 시작했으나 **09-30 09:28 CDT 에 main 세션이 중단**했다: ρ 32 는 SNR 하나에 ≈ 6.4–6.8 h (−3 dB 23092–24351 s), 7 SNR × 5 데이터셋 ≈ 2 일이고 HISNR 과 CPU 를 다툰다 (`logs/sparse_ext.log`). 중단은 비용 때문이며 ρ 32 의 NMSE 는 저장·열람되지 않았다 (스크립트는 끝에만 쓴다).
- 이미 본 v2b 값으로 본 크기: ρ 8 → 16 의 SNR 평균 개선은 SBL ≤ 0.05 dB, OMP ≤ 0.20 dB (D3; 나머지 ≤ 0.12), −3 dB 에서는 둘 다 ≤ 0.08 dB — 포화에 가깝다. 그러나 ρ 32 가 더 낫지 않다는 증거는 아니다.
- **SBL 만의 ρ 32 확장은 데이터셋당 ≈ 0.5 h 였을 것이나 하지 않았다** (v2 재검토 1 회차 stats-fair 실측: `gamma_path` 50 단계 ρ 32 1.01 s (N 32, 2 스레드) × 256 표본 × 7 SNR; ρ 8 → 16 이득이 SBL ≤ 0.05 dB). ρ 32 확장 비용은 거의 전부 OMP 쪽이다.
- **OMP ρ 32 는 테스트 실행 자체가 불가능하다**: OMP-pilot 이 만드는 M × M `AᴴGA` (C2 ρ 32: M = 32² · 32 = 32768, complex128) 가 워커당 ≈ 17 GB, 192 워커 ≈ 3.3 TB (MemAvailable ≈ 1 TB).
- 처리 (v2 에서 고정): **ρ 16 을 쓴다; 라벨·예측·판정은 바꾸지 않는다**; 원고와 §6 에 "ρ 는 격자 끝 16 (확장 규칙 2 회째를 비용으로 중단)" 을 적는다. C6 도 같은 처리 — C6 도 ρ_SBL·ρ_OMP 모두 끝값 16 (§5.2 표).

## 6. 결과 (이 절은 추가만 한다)

### 6.1 결과 (기록 2026-09-30 20:30 CDT (= 10-01 10:30 KST), Opus 5.5 — 전사만, 해석 없음; 원본 `results/review_next/pairB_SP<suf>.txt`, `SP<suf>_accept.txt`, `run_manifest_SP<suf>.json`, 로그 `logs/run_sparse16e4.log`·`logs/run_D2_SP<suf>.log` (청크별 BLER 줄은 옮기지 않음), raw `raw_SP<suf>/`; 테스트 NMSE@1 과 raw 검사는 이 기록에서 raw 로 계산 — 아래 방법; 재현: `prereg_audit_2026-10-01/sparse_recompute.out` §1·§4, 기록자 스크립트 사본 `sparse_transcriber_check_sp.{py,out}`)

**동결 커밋 = 실행 커밋**: 02dafa1c (sbl 팁 be0a5540 → main 병합 커밋; DECISIONS 동결 줄). **실행**: `bash code/run_sparse16e4.sh` (인자 없음 = 6 행) 09-30 19:04 CDT `start (git 02dafa1c) rows: all` (run_sparse16e4.log:1; 전제 검사 — conf/code·Demo 청결, 이 문서·DECISIONS tracked·clean — 통과), 20:22 CDT `SPARSE_DONE ok=6 fail=0` (:50), `SPARSE_EXIT=0` (:51). `start` 1 회, ABORT·INVALID·resume·게이트 대기 줄 없음. 실행 구간 중 main 커밋 없음 (이 기록 시점 HEAD = 02dafa1c). **C6 게이트 건너뜀**: §5.2 (가) 로 NR16 행 PSHA = `3958df589e385522` (스크립트 21 행) — 게이트 블록 (34–39 행) 은 pick 파일이 없고 PSHA 가 `-` 일 때만 돌며, 로그에 `waiting`·`copied` 줄이 없다; NR16 은 C2 와 같은 sha·git 추적 + clean·규칙 재현 검사를 거쳤다 (:42).

**raw (기록자 확인, 단일 프로세스·GPU 숨김)**: 6 태그 × npz 448 (= 7 SNR × 64 청크, 청크 40, skip 0..2520, SNR 당 시행 2560) — `run|git` 2688/2688 이 02dafa1c; `meta|sparse` 가 그 SNR 의 pick 값과 다른 청크 0; `meta|stagec_ckpt_id` 키 0; `<arm>|failed` 키 0; 새 3 arm `blk_err` 비유한 값 0 (16 반복 전부). base·PIL·ALD raw: `pairB_SP<suf>.txt` 머리말 `integrity: OK` 6/6, 그 manifest-head·chunks-sha 18 개는 STATIC16e4 §6.1 머리말과 같다 (`extra0=02dafa1c`).

| 행 (태그) | pick · tune sha256[:16] · 규칙 재현 · 메모리 가드 (로그 줄 그대로) | runner (`run_D2_SP<suf>.log:452`) · 청크 mtime 첫–끝 (CDT) | run_manifest · 수용 (`SP<suf>_accept.txt:1` 그대로) | 새 arm 예외 시행 | `meta\|sparse` 검사 | pair_baselines |
|---|---|---|---|---|---|---|
| D2 C2 (SPB16e4k) | `2a6d79a23b6b6501` · `6f1e19bd6ce05bd3` · rule-reproduced=True · need ~264 GB, available 1029 GB (:2) | 9.5 min · 19:06:50–19:13:39 | 19:13 rc=0 (:5; written 10-01 09:13:43 KST) · 19:13 rc=0 **ACCEPT: OK -- SPB16e4k** (:6) | {'SBL-loop': 0, 'SBL-pilot': 0, 'OMP-pilot': 0} (:7) | 0 mismatching chunks (:8) | 19:14 rc=0 (:9) |
| D3 (SPD3) | `afdb48498c76b88c` · `42b078018bea5471` · True · ~264 GB, 1028 GB (:10) | 9.2 min · 19:15:56–19:23:23 | 19:23 rc=0 (:13; 09:23:27 KST) · 19:23 rc=0 **ACCEPT: OK -- SPD3** (:14) | 0 · 0 · 0 (:15) | 0 (:16) | 19:23 rc=0 (:17) |
| SV8e (SPSV) | `72a6500e72950141` · `1b737191fdf8e668` · True · ~264 GB, 1028 GB (:18) | 6.2 min · 19:25:20–19:30:06 | 19:30 rc=0 (:21; 09:30:10 KST) · 19:30 rc=0 **ACCEPT: OK -- SPSV** (:22) | 0 · 0 · 0 (:23) | 0 (:24) | 19:30 rc=0 (:25) |
| UMi28 (SPU28) | `3d27f1bb72865fa5` · `4099975241c07a0d` · True · ~264 GB, 1028 GB (:26) | 4.8 min · 19:31:44–19:35:24 | 19:35 rc=0 (:29; 09:35:29 KST) · 19:35 rc=0 **ACCEPT: OK -- SPU28** (:30) | 0 · 0 · 0 (:31) | 0 (:32) | 19:35 rc=0 (:33) |
| MIX3 (SPMX) | `baffec3e463ad6b3` · `b02e6acacfb7aa5e` · True · ~264 GB, 1028 GB (:34) | 7.6 min · 19:37:53–19:43:31 | 19:43 rc=0 (:37; 09:43:36 KST) · 19:43 rc=0 **ACCEPT: OK -- SPMX** (:38) | 0 · 0 · 0 (:39) | 0 (:40) | 19:44 rc=0 (:41) |
| D2 C6 (SPNR16) | `3958df589e385522` · `81dba7612d964a06` · True · ~882 GB, 1028 GB (:42) | 37.6 min · 19:53:46–20:21:42 | 20:21 rc=0 (:45; 10:21:46 KST) · 20:21 rc=0 **ACCEPT: OK -- SPNR16** (:46) | 0 · 0 · 0 (:47) | 0 (:48) | 20:22 rc=0 (:49) |

(괄호 `:n` = `logs/run_sparse16e4.log` 의 줄. pick·tune sha 는 §5.1·§5.2 와 같다. 규칙 재현 줄은 tune JSON 의 prior·cell = 그 행, n = 256·격자 = v2b assert 를 통과해야 찍힌다 — 스크립트 47–48 행; sha 검사·git 추적 + clean 검사 (41–43 행) 는 ABORT 줄 없음으로 통과.)

**매니페스트 요지** (`run_manifest_SP<suf>.json`): git 02dafa1c (4 행), n_raw_files 448 (8 행), config_hash `ba9bc0a2cb5fbb84` (C2 다섯) / `a936007de9918754` (C6) (9 행), arms OMP-pilot·R5-genie·SBL-loop·SBL-pilot, `stagec_ckpt_id` "(none)" (112/113 행), 적합 링크 `gmm_fits_D2_SP<suf>` → `gmm_fits_D2_{B16e4k, D3B16e4, SVB16e4, U28B16e4, MXB16e4, NR16B16e4}` (b\* = kron K 1024 / kron 4096 / gmm256 / kron 4096 / kron 4096 / kron 4096), cpu_count 192.

**C6 pick (`results/sparse/pick_S2_C6.json`, §5.2 와 같음)**: ρ_SBL 16 (끝), ρ_OMP 16 (끝); SNR −3..+15 dB 의 n_em 3·5·5·5·5·10·10, L 4·6·6·8·8·8·12; SNR 별 끝 플래그 (`edge_sbl`·`edge_omp`) 14 칸 모두 false.

**표 B — 새 arm `X → V1` (`pairB_SP<suf>.txt` 그대로; 판정점 · 점별 a:b · pooled · 라벨; 1차 R_X (−3 dB), 2차 R_X (판정점), 절대 격차 F_X − F_V1 (−3 dB, /2560), SNR@0.1 격차 X − V1 [90%] 는 보고 전용)**

| 데이터셋 | X | 판정점 | 점별 a:b | pooled | 라벨 | R_X −3 dB [90%] | R_X 판정점 [90%] | 절대 격차 | SNR@0.1 격차 | 출처 줄 |
|---|---|---|---|---|---|---|---|---|---|---|
| D2 C2 | SBL-loop | −3/+0/+3 | 381:47 · 148:14 · 59:11 | 588:72 | **(i)** 3/3 | 0.540 [0.503, 0.579] | 0.587 [0.554, 0.618] | 334 | +1.86 [+1.64, +2.10] | SPB16e4k:96–102 |
| D2 C2 | SBL-pilot | −3/+0/+3 | 589:26 · 171:15 · 51:11 | 811:52 | **(i)** 3/3 | 0.665 [0.635, 0.694] | 0.676 [0.651, 0.702] | 563 | +2.12 [+1.90, +2.35] | :103–109 |
| D2 C2 | OMP-pilot | +0/+3/+6 | 263:9 · 124:8 · 64:3 | 451:20 | **(i)** 3/3 | 0.697 [0.669, 0.723] | 0.834 [0.802, 0.863] | 652 | +3.24 [+2.99, +3.51] | :110–116 |
| D3 | SBL-loop | +0/+3/+6 | 252:39 · 137:24 · 85:6 | 474:69 | **(i)** 3/3 | 0.406 [0.375, 0.438] | 0.525 [0.491, 0.560] | 352 | +1.62 [+1.35, +1.97] | SPD3:95–101 |
| D3 | SBL-pilot | +0/+3/+6 | 358:27 · 176:18 · 100:10 | 634:55 | **(i)** 3/3 | 0.506 [0.479, 0.534] | 0.613 [0.583, 0.641] | 528 | +2.35 [+1.97, +2.68] | :102–108 |
| D3 | OMP-pilot | +3/+6/+9 | 253:12 · 159:2 · 94:5 | 506:19 | **(i)** 3/3 | 0.528 [0.500, 0.555] | 0.792 [0.760, 0.823] | 575 | +3.95 [+3.52, +4.51] | :109–115 |
| SV8e | SBL-loop | −3/+0 | 209:37 · 47:5 | 256:42 | **(iv)** (POWERED=False, 판정점 2; V1 쪽 적음 2/2) | 0.317 [0.276, 0.355] | 0.341 [0.303, 0.377] (2 점) | 172 | +0.67 [+0.56, +0.78] | SPSV:95–101 |
| SV8e | SBL-pilot | −3/+0/+3 | 543:19 · 101:4 · 19:0 | 663:23 | **(i)** 3/3 | 0.585 [0.557, 0.614] | 0.604 [0.579, 0.630] | 524 | +1.44 [+1.31, +1.59] | :102–108 |
| SV8e | OMP-pilot | −3/+0/+3 | 1102:11 · 336:3 · 60:1 | 1498:15 | **(i)** 3/3 | 0.746 [0.727, 0.765] | 0.780 [0.764, 0.795] | 1091 | +3.04 [+2.89, +3.20] | :109–115 |
| UMi28 | SBL-loop | +3/+6/+9 | 154:25 · 97:21 · 56:10 | 307:56 | **(i)** 3/3 | 0.262 [0.230, 0.292] | 0.336 [0.299, 0.370] | 225 | +1.45 [+1.11, +1.76] | SPU28:95–101 |
| UMi28 | SBL-pilot | +3/+6/+9 | 201:16 · 113:21 · 74:12 | 388:49 | **(i)** 3/3 | 0.447 [0.421, 0.471] | 0.406 [0.373, 0.437] | 512 | +1.75 [+1.39, +2.09] | :102–108 |
| UMi28 | OMP-pilot | +6/+9/+12 | 282:5 · 177:3 · 110:2 | 569:10 | **(i)** 3/3 | 0.629 [0.609, 0.648] | 0.673 [0.645, 0.700] | 1076 | +4.28 [+3.65, +4.80] | :109–115 |
| MIX3 | SBL-loop | +3/+6/+9 | 190:33 · 136:12 · 90:11 | 416:56 | **(i)** 3/3 | 0.245 [0.216, 0.273] | 0.456 [0.421, 0.490] | 219 | +2.42 [+2.06, +2.80] | SPMX:95–101 |
| MIX3 | SBL-pilot | +3/+6/+9 | 256:29 · 169:11 · 98:9 | 523:49 | **(i)** 3/3 | 0.404 [0.378, 0.428] | 0.524 [0.493, 0.555] | 457 | +2.84 [+2.45, +3.28] | :102–108 |
| MIX3 | OMP-pilot | +6/+9/+12 | 408:0 · 257:3 · 171:5 | 836:8 | **(i)** 3/3 | 0.561 [0.539, 0.582] | 0.789 [0.766, 0.812] | 861 | +6.09 [+5.60, +6.65] | :109–115 |
| D2 C6 | SBL-loop | −3/+0/+3 | 203:5 · 83:4 · 44:2 | 330:11 | **(i)** 3/3 | 0.865 [0.820, 0.906] | 0.884 [0.847, 0.916] | 198 | n/a (<= −3 vs <= −3) — extend the SNR grid | SPNR16:95–101 |
| D2 C6 | SBL-pilot | −3/+0/+3 | 245:7 · 92:5 · 46:2 | 383:14 | **(i)** 3/3 | 0.885 [0.847, 0.920] | 0.898 [0.867, 0.926] | 238 | >= +0.38 dB (M-ours-dscore-C-V1 is already below 0.1 at the lowest grid SNR) | :102–108 |
| D2 C6 | OMP-pilot | −3/+0/+3 | 163:9 · 102:2 · 57:1 | 322:12 | **(i)** 3/3 | 0.832 [0.777, 0.884] | 0.881 [0.845, 0.914] | 154 | n/a (<= −3 vs <= −3) — extend the SNR grid | :109–115 |

(라벨의 "3/3" = 그 줄의 `second arm fewer at 3/3, first arm fewer at 0/3`, 모두 POWERED=True.)

**데이터셋별 요약 (`SUMMARY-B`·16 개 요약·X\*·문장 조건 줄 그대로; SPB16e4k 는 117·119–122 행, 나머지 다섯은 116·118–121 행)**:

| 데이터셋 | 원 b\* (`--expect-bstar` 일치) | SUMMARY-B (15) (i) · (ii) · 판정 못함 | 16 개 (b\* + 𝔅 15) | (i) 아닌 X | X\* (F −3 dB) · R_{X\*} [90%] | "전부" 문장 조건 |
|---|---|---|---|---|---|---|
| D2 C2 (헤드라인) | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (623) · 0.470 [0.427, 0.512] | MET |
| D3 | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (1298) · 0.367 [0.335, 0.399] | MET |
| SV8e | (iv) | 11 · 0 · 4 | 11 · 0 · 5 | b\* (iv), M-ours-bstar-scalar (iv), M-ours-gmm32 (iv), V1-pilot (iv), SBL-loop (iv) | M-ours-bstar (464) · 0.143 [0.095, 0.188] | NOT met |
| UMi28 | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (1270) · 0.062 [0.033, 0.089] | MET |
| MIX3 | (i) | 15 · 0 · 0 | 16 · 0 · 0 | — | M-ours-bstar (1421) · 0.090 [0.062, 0.117] | MET |
| D2 C6 | (i) | 14 · 0 · 1 | 15 · 0 · 1 | V1-pilot (iv) | V1-pilot (83) · 0.492 [0.355, 0.630] | NOT met |

- 인용 13 라벨 (b\* + 𝔅 12): pair_baselines rc 0 × 6 = `--expect` 6 × 13 일치 (드리프트 없음); 각 파일의 13 arm 블록 (91 행, `M-ours-bstar ->` ~ `ALDv-pilot` 블록 끝) 이 `pairB_ST<TAG>.txt` 의 같은 블록과 바이트 동일 (기록자 diff, 6/6). X\*·R_{X\*} 는 6 데이터셋 모두 STATIC16e4 §6.1 값과 같다.

**주 라벨 (D2 C2)**: SBL-loop·SBL-pilot·OMP-pilot 모두 (i) (위 표) → **(A) "V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패"** (A1 = `SBL-loop → V1` (i) 588:72).

**"전부" 문장 (16 개)**: 원 b\* (i)·15 개 모두 (i)·(ii) 0·R_{X\*} CI 하한 > 0 → **D2 C2·D3·UMi28·MIX3 충족** → "데이터셋 d 에서 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다" (d = D2 C2, D3, UMi28, MIX3). C6·SV8e 불충족 (§1: STATIC16e4 의 (iv) 로 결과와 무관하게 불가능).

**집계 (개수 서술만, 보정 없음)**: 새 18 라벨 중 (i) 17, (iv) 1 (SV8e SBL-loop), (ii) 0. 인용 78 라벨 (b\* 6 + 𝔅 72) 재계산·대조 일치. "전부" 문장 4/6 (가능하던 4 곳 모두).

**§3 예측 채점**:

| # | 예측 | 결정하는 수 | 채점 |
|---|---|---|---|
| 1 | 주 라벨 D2 C2 = (A) | SBL-loop (i) 588:72, SBL-pilot (i) 811:52, OMP-pilot (i) 451:20 (각 3/3) → (A) | ✓ |
| 2 (D3) | 새 3 개 모두 (i) | SBL-loop (i) 474:69, SBL-pilot (i) 634:55, OMP-pilot (i) 506:19 → 3/3 | ✓ |
| 2 (C6) | 새 3 개 모두 (i) | SBL-loop (i) 330:11, SBL-pilot (i) 383:14, OMP-pilot (i) 322:12 → 3/3 | ✓ |
| 3 | UMi28·MIX3·SV8e: OMP-pilot → V1 셋 모두 (i) | UMi28 (i) 569:10, MIX3 (i) 836:8, SV8e (i) 1498:15 → 3/3 | ✓ |
| 4 | UMi28·MIX3·SV8e: SBL-loop → V1 이 (i) 아닌 데이터셋 ≥ 1 | UMi28 (i) 307:56, MIX3 (i) 416:56, SV8e **(iv)** 256:42 (POWERED=False, 판정점 2) → 1 개 | ✓ |
| 5 | 새 18 라벨 중 (ii) ≤ 1 | (ii) 0 | ✓ |
| 6 | 보고 전용 `b* → SBL-loop` (D2 C2) | 계산하지 않음 — 등록 명령 `pair_baselines` 가 이 쌍을 내지 않고, 이 기록은 결과 뒤 코드를 쓰지 않았다 (§1 보고 전용, §3 6) | 채점 안 함 |
| 7 | 빗나갈 경로 | 수용·무결성 실패 0, `--expect` 불일치 0, C6 게이트·메모리 가드 ABORT 0, pick·tune 미추적/dirty·규칙 재현 불일치 0 | 예측 항목 아님 |

합계: 적중 6, 빗나감 0 (채점 안 함 1 — 6).

**보고 전용** (§1; 판정 아님):

(a) 새 arm 의 R_X (1차·2차)·절대 격차·SNR@0.1 격차 → 위 표 B. 전 arm 의 SNR 별 실패 수·NMSE@16 중앙값 → 각 `pairB_SP<suf>.txt` (`BLER@16 failures` 줄, `report-only, median NMSE@16` 줄).

(b) −3 dB 실패 수 (`BLER@16 failures / n` 줄의 −3 dB 칸, n = 2560; SPB16e4k 124–126·139–141 행, 나머지 123–125·138–140 행):

| 데이터셋 | R5-genie | V1 | b\* | SBL-loop | SBL-pilot | OMP-pilot |
|---|---|---|---|---|---|---|
| D2 C2 | 87 | 371 | 623 | 705 | 934 | 1023 |
| D3 | 485 | 1000 | 1298 | 1352 | 1528 | 1575 |
| SV8e | 31 | 402 | 464 | 574 | 926 | 1493 |
| UMi28 | 594 | 1228 | 1270 | 1453 | 1740 | 2304 |
| MIX3 | 679 | 1354 | 1421 | 1573 | 1811 | 2215 |
| D2 C6 | 22 | 53 | 184 | 251 | 291 | 207 |

(c) 새 arm 의 NMSE@16 중앙값 (`report-only, median NMSE@16 of the channel estimate per SNR` 줄 그대로; SPB16e4k 161–163 행, 나머지 160–162 행):

| 데이터셋 | arm | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|---|
| D2 C2 | SBL-loop | 8.43e-02 | 3.86e-02 | 1.95e-02 | 9.61e-03 | 4.69e-03 | 2.37e-03 | 1.21e-03 |
| D2 C2 | SBL-pilot | 2.41e-01 | 1.26e-01 | 6.61e-02 | 3.33e-02 | 1.67e-02 | 8.36e-03 | 4.31e-03 |
| D2 C2 | OMP-pilot | 2.37e-01 | 1.34e-01 | 7.69e-02 | 4.23e-02 | 2.44e-02 | 1.46e-02 | 7.88e-03 |
| D3 | SBL-loop | 1.42e-01 | 4.52e-02 | 2.16e-02 | 1.08e-02 | 5.27e-03 | 2.74e-03 | 1.38e-03 |
| D3 | SBL-pilot | 2.56e-01 | 1.35e-01 | 7.00e-02 | 3.68e-02 | 1.84e-02 | 9.56e-03 | 4.84e-03 |
| D3 | OMP-pilot | 2.44e-01 | 1.38e-01 | 7.86e-02 | 4.58e-02 | 2.68e-02 | 1.51e-02 | 8.61e-03 |
| SV8e | SBL-loop | 1.16e-01 | 5.82e-02 | 3.06e-02 | 1.59e-02 | 8.20e-03 | 4.33e-03 | 2.15e-03 |
| SV8e | SBL-pilot | 3.06e-01 | 1.72e-01 | 9.51e-02 | 5.13e-02 | 2.68e-02 | 1.43e-02 | 7.22e-03 |
| SV8e | OMP-pilot | 4.32e-01 | 2.47e-01 | 1.29e-01 | 6.46e-02 | 3.20e-02 | 1.64e-02 | 8.05e-03 |
| UMi28 | SBL-loop | 1.58e-01 | 6.69e-02 | 3.15e-02 | 1.50e-02 | 7.45e-03 | 3.74e-03 | 1.96e-03 |
| UMi28 | SBL-pilot | 2.54e-01 | 1.44e-01 | 7.89e-02 | 4.26e-02 | 2.29e-02 | 1.19e-02 | 6.29e-03 |
| UMi28 | OMP-pilot | 3.36e-01 | 2.15e-01 | 1.27e-01 | 6.44e-02 | 3.21e-02 | 1.60e-02 | 8.01e-03 |
| MIX3 | SBL-loop | 1.65e-01 | 6.57e-02 | 2.96e-02 | 1.37e-02 | 6.86e-03 | 3.54e-03 | 1.80e-03 |
| MIX3 | SBL-pilot | 2.50e-01 | 1.39e-01 | 7.53e-02 | 3.87e-02 | 2.10e-02 | 1.11e-02 | 5.89e-03 |
| MIX3 | OMP-pilot | 3.00e-01 | 1.85e-01 | 1.14e-01 | 6.40e-02 | 3.27e-02 | 1.64e-02 | 8.29e-03 |
| D2 C6 | SBL-loop | 6.24e-02 | 2.92e-02 | 1.47e-02 | 7.50e-03 | 3.82e-03 | 1.89e-03 | 9.41e-04 |
| D2 C6 | SBL-pilot | 2.02e-01 | 1.04e-01 | 5.25e-02 | 2.69e-02 | 1.36e-02 | 6.87e-03 | 3.43e-03 |
| D2 C6 | OMP-pilot | 1.41e-01 | 8.28e-02 | 4.41e-02 | 2.79e-02 | 1.51e-02 | 8.48e-03 | 5.42e-03 |

(d) **SBL-loop NMSE@16 − SBL-pilot NMSE** (dB, SNR 별 = 10·log10 (SBL-loop 중앙값 / SBL-pilot 중앙값); 입력은 (c) 의 출력 값 (유효숫자 3 자리) 그대로; §2 의 n_em 문장과 함께 읽는다):

| 데이터셋 | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|
| D2 C2 | −4.56 | −5.14 | −5.30 | −5.40 | −5.52 | −5.47 | −5.52 |
| D3 | −2.56 | −4.75 | −5.11 | −5.32 | −5.43 | −5.43 | −5.45 |
| SV8e | −4.21 | −4.71 | −4.92 | −5.09 | −5.14 | −5.19 | −5.26 |
| UMi28 | −2.06 | −3.33 | −3.99 | −4.53 | −4.88 | −5.03 | −5.06 |
| MIX3 | −1.80 | −3.25 | −4.06 | −4.51 | −4.86 | −4.96 | −5.15 |
| D2 C6 | −5.10 | −5.52 | −5.53 | −5.55 | −5.51 | −5.60 | −5.62 |

(e) **테스트 파일럿 전용 NMSE@1 과 §5 개발 NMSE 의 차** (정의가 달라 예측으로 채점하지 않는다 — §1). 방법: 테스트 = `raw_SP<suf>` 의 `<arm>|nmse[:, 0]` (반복 1) 을 SNR 별 2560 시행에서 평균한 값의 10·log10 (모두 유한); 개발 = pick JSON 의 `nmse_sbl_db` (SBL-pilot) / `nmse_omp_db` (OMP-pilot) (= §5 표, 10·log10 Σ‖e‖²/Σ‖h‖²). 칸 = 테스트 dB (테스트 − 개발):

| 데이터셋 | arm | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|---|
| D2 C2 | SBL-pilot | −5.99 (+0.14) | −8.79 (−0.09) | −11.61 (+0.13) | −14.55 (+0.07) | −17.55 (+0.20) | −20.54 (+0.16) | −23.46 (+0.02) |
| D2 C2 | OMP-pilot | −5.87 (+0.15) | −8.45 (−0.16) | −10.88 (−0.05) | −13.37 (+0.12) | −15.83 (+0.14) | −18.15 (+0.14) | −20.90 (+0.06) |
| D3 | SBL-pilot | −4.95 (+1.62) | −7.72 (+1.59) | −10.60 (+1.59) | −13.19 (+1.17) | −16.36 (+1.41) | −19.12 (+1.89) | −22.18 (+1.34) |
| D3 | OMP-pilot | −4.80 (+1.76) | −7.47 (+1.63) | −10.02 (+1.40) | −12.27 (+1.05) | −14.77 (+1.36) | −17.25 (+1.77) | −19.73 (+1.26) |
| SV8e | SBL-pilot | −4.89 (+0.33) | −7.36 (+0.40) | −9.98 (+0.35) | −12.62 (+0.55) | −15.42 (+0.27) | −18.19 (+0.41) | −21.14 (+0.39) |
| SV8e | OMP-pilot | −3.38 (+0.43) | −5.80 (+0.45) | −8.64 (+0.42) | −11.61 (+0.55) | −14.64 (+0.27) | −17.60 (+0.37) | −20.68 (+0.39) |
| UMi28 | SBL-pilot | −5.57 (+0.13) | −8.04 (+0.51) | −10.64 (+0.57) | −13.26 (+0.46) | −15.99 (+0.28) | −18.80 (+0.54) | −21.63 (+0.47) |
| UMi28 | OMP-pilot | −4.17 (+0.04) | −6.13 (+0.41) | −8.65 (+0.59) | −11.60 (+0.51) | −14.63 (+0.31) | −17.64 (+0.46) | −20.65 (+0.55) |
| MIX3 | SBL-pilot | −5.47 (+0.80) | −7.99 (+0.98) | −10.67 (+0.62) | −13.49 (+0.51) | −16.20 (+0.78) | −18.97 (+0.73) | −21.79 (+0.67) |
| MIX3 | OMP-pilot | −4.51 (+0.72) | −6.43 (+0.85) | −8.71 (+0.67) | −11.36 (+0.64) | −14.29 (+0.79) | −17.32 (+0.74) | −20.30 (+0.73) |
| D2 C6 | SBL-pilot | −6.83 (+0.05) | −9.72 (+0.03) | −12.70 (+0.08) | −15.59 (+0.03) | −18.56 (+0.02) | −21.52 (+0.08) | −24.55 (−0.02) |
| D2 C6 | OMP-pilot | −8.30 (+0.01) | −10.63 (+0.02) | −13.28 (+0.16) | −15.37 (+0.08) | −17.96 (+0.15) | −20.20 (+0.07) | −22.50 (−0.08) |

(차는 반올림 전 값의 차.)

(f) `b* → SBL-loop` 표 B: 계산하지 않음 (예측 6 행).

**캐비엇 (§2·§5.3 이 적으라고 정한 것)**:
- **ρ 는 격자 끝 16 (확장 규칙 2 회째를 비용으로 중단)** (§5.3). pick 의 `edge_rho_*`: SBL 은 D2 C2·D3·SV8e·MIX3·C6 에서 ρ 16 끝 (UMi28 은 ρ_SBL 8 내부), OMP 는 6 데이터셋 모두 ρ 16 끝. SNR 별 끝 플래그는 C2 35 칸 × 2·C6 7 칸 × 2 모두 false.
- **OMP-pilot = 파일럿 LS 인 점 (L = N, §2)**: D2 C2 +15 dB; SV8e +3..+15 dB; UMi28 +3..+15 dB; MIX3 +6..+15 dB (L = 32 = N) — 15 점; D3 없음; **C6 없음** (L ≤ 12 < N = 64). OMP-pilot 쌍의 판정점 중 이 점: D2 C2 (+0/+3/+6) 없음, D3 (+3/+6/+9) 없음, SV8e (−3/+0/+3) +3 dB, UMi28 (+6/+9/+12) 셋 모두, MIX3 (+6/+9/+12) 셋 모두, C6 없음. §2 대로 이 점의 OMP-pilot 결과는 원고에서 "희소 복원" 으로 부르지 않는다.
- **새 arm 예외 시행**: 6 행 × 3 arm 모두 0 (로그 :7·:15·:23·:31·:39·:47; raw 의 `|failed` 키 0) → §2 의 "개수를 라벨 문장에 함께 적는다" 규칙이 적용되는 라벨 없음.
- SBL-loop 의 n_em 은 파일럿 개발 NMSE 로 고른 값 (루프 전용 튜닝 없음) — §2 문장 그대로; 보고 전용 (d).

**편차·주의 (사실만)**:
- §1 "실행 중 다른 CPU 작업 없음 (예외 …)" 대조 — 기록자 `ps` 스냅숏 09-30 20:25 CDT (SPARSE_DONE 3 분 뒤; 파일로 남기지 않음 — 같은 프로세스 집합의 20:27 CDT 스냅숏은 `prereg_audit_2026-10-01/sparse_ps_snapshot_transcriber_2027CDT.txt` (누적 %CPU 96.9–99.6), 감사 시각 20:41 CDT 의 `ps`·`/proc/<pid>/cwd` (= `~/t2_wtS/conf`)·tmux 는 같은 폴더 `sparse_concurrent_processes.txt`; 감사 §6.2) 에서 실행 구간 (19:04–20:22 CDT) 전에 시작해 아직 도는 프로세스: (a) 2단계 GPU 적합 `code/fit_gpu.py 32 kron 2048 160000 NR32B16e4 --restart 0/1/2` 와 `… U28NR32B16e4 --restart 0/1/2 --prior UMi28` 6 개 (`~/t2_wtS/conf`, tmux job_g0–g5, GPU 0–5; 시작 09-30 11:13:52·11:22:00·11:33:13·16:03:20·16:41:02·16:51:09 CDT; 누적 %CPU 96.8–99.5 = 각 코어 1 개), bash 루프 `gpu_sched.sh`·`edge_rule.sh` (10:43:20 CDT)·`batched_prefix.sh` (15:19:59 CDT) — **§1 예외 목록 안**. (b) 상시 도구 프로세스: Claude Code 세션 (`claude`, tmux dev), claude-mem worker (bun)·chroma-mcp (python, 누적 %CPU 13.8) — 09-28 22:42–22:43 CDT 부터; 실험 작업이 아니며 §1 예외 목록에 이름이 없다. (c) S2 C6 튜닝 프로세스 없음 (§5.2: 09-30 18:53 CDT 종료, tmux sparsetune 도 그때 종료); `~/t2_wtSBL` 은 있다 (게이트를 건너뛰어 읽히지 않음). (d) 구간 안에서 시작·종료한 프로세스는 스냅숏에 보이지 않으므로 하한이다; `fit_gpu.py --merge` 실행 여부는 확인하지 못했다. 구간 중 main 작업 트리에 쓰인 파일은 이 실행의 산출 (raw_SP\*, 로그 7 개, accept·pairB·manifest 18 개, 적합 링크 `results/gmm_fits_D2_SP<suf>` 6 개 — 스크립트 60 행) 과 `code/__pycache__` (arms·sparse_tune .pyc, 19:04 CDT — 스크립트의 규칙 재현 블록이 import), 그리고 `.git/index` (19:04:04 CDT; 스크립트의 `git status`·`ls-files` 호출이 새로 씀, 커밋 아님) 뿐 (기록자 `find -newermt`; 이 문서의 mtime 19:03:50 CDT 는 start 직전이며 내용은 HEAD 와 같다 — `git diff` 없음).
- 소요: runner C2 9.5·9.2·6.2·4.8·7.6 min, C6 37.6 min; 스크립트 전체 19:04–20:22 CDT (1 h 18 min). §1 비용 추정은 C2 행당 ≈ 10 분 안팎, C6 ≈ 15 분–1.5 h + 수신기 EP 부분.
- 스크립트 로그에는 행 시작 시각이 없다 — 행별 시각은 runner 로그 끝 줄의 소요, 청크 npz mtime, 로그의 run_manifest·acceptance·pair_baselines 시각.
- `pairB_SPB16e4k.txt` 에만 머리말 2 행 `# base V1 checkpoint id: manifest (none), file d2sx_N160000_a1.pt 4443921ce8d5c4a1` 가 있다 (`pairB_STB16e4k.txt:2` 와 같은 줄) — 그 파일의 줄 번호는 다른 다섯보다 1 크다.
- runner 는 `results/tables_D2_SP*.txt`·`guard_D2_SP*.txt` 를 만들지 않았다 (runner 끝 줄은 `runner.py analysis` 안내만; 매니페스트 `output_paths` 에 경로만 적힘). §1 의 등록 출력은 pairB·accept·manifest.
- (d) 는 출력 값 (유효숫자 3 자리) 에서 계산했으므로 반올림 오차가 있다; (e) 의 테스트 값은 이 기록에서 raw 로 계산했다 (스크립트 출력 아님).
- p 값은 서술용 (§1 다중성: 보정 없음).

### 6.2 기록 감사 (수치 재계산 + 규칙·출처 감사, Fable 5.1 서브에이전트, 독립·읽기 전용; 2026-09-30 20:54 CDT = 10-01 10:54 KST; `prereg_audit_2026-10-01/audit_SPARSE16e4.md` (`sparse_recompute.py/.out`, `sparse_concurrent_processes.txt`, `sparse_ps_snapshot_transcriber_2027CDT.txt`, `sparse_transcriber_check_sp.{py,out}`); raw npz 에서 독립 재계산 — pair_baselines·analysis·eval_accept 미호출)

수치·라벨·예측 채점 오류 **0** (2153 검사, mismatches 0), 규칙 위반 **0** (§0–§6 조건 14 항목). 다시 계산한 것: SP raw 6 태그 무결성 (npz 448 = 7 SNR × {(40k, 40)}, `run|git` 02dafa1c·iters 16·seed 20260926, meta 5 키 = base raw, `meta|sparse` = pick 불일치 0, `meta|stagec_ckpt_id` 키 0, `<arm>|failed` 키 0·비유한 0 (3 arm × 16 반복), R5-genie 4 키 = base 7/7, n 2560); pick·tune sha256[:16] 12 개·tune v2b 6 개·규칙 재현 6/6 (동결 커밋의 `sparse_tune.per_snr_pick` 을 tune JSON 에 다시 적용, 끝 플래그까지)·메모리 가드 264 GB × 5 / 882 GB; 새 18 라벨 ((i) 17·(iv) 1 (SV8e SBL-loop, 판정점 2)·(ii) 0) 과 표 B 18 × 10 칸 (판정점·a:b·pooled·라벨·R_X 1차/2차 (paired bootstrap B 2000, rng 20260926)·절대 격차·SNR@0.1 격차 (seed 20260925)·출처 줄); 인용 13 라벨 × 6 = 78 (= STATIC, `--expect`)·13 arm 블록 바이트 동일 6/6·출처 머리말 18; 데이터셋별 요약 6 행 (X\*·R_{X\*}·"전부" 문장 MET 4/6); (b) (c) (d) (e) 표 288 칸; §3 예측 6/6 (6 채점 안 함); 매니페스트·수용 파일·runner 로그·로그 줄 문자열·스크립트 줄 번호; git (§0–§5 불변, 작업 트리 +165/−0 hunk 1 개 `## 6.` 뒤, 실행 구간 main 커밋 0)·KST↔CDT; EXPERIMENTS 행·DECISIONS 줄의 수열. 위생 정정 3 건 (전부 선택; 수치·라벨·채점 불변) — 전부 반영:
1. [출처 보존] §6.1 편차 첫 항목: 인용한 20:25 CDT `ps` 스냅숏은 파일이 없음 → 같은 프로세스 집합의 20:27 CDT 스냅숏 사본 (`sparse_ps_snapshot_transcriber_2027CDT.txt`, 누적 %CPU 96.9–99.6) 과 감사 시각 스냅숏 (`sparse_concurrent_processes.txt`) 을 인용하도록 문구 추가.
2. [공개 보강] §6.1 편차 첫 항목 끝: 구간 중 쓰인 파일 목록에 적합 링크 `results/gmm_fits_D2_SP<suf>` 6 개 (스크립트 60 행) 와 `.git/index` (19:04:04 CDT; 스크립트의 `git status`·`ls-files` 호출, 커밋 아님) 추가.
3. [출처] §6.1 머리말: 테스트 NMSE@1·raw 검사의 재현 출처 `sparse_recompute.out` §1·§4 와 기록자 스크립트 사본 `sparse_transcriber_check_sp.{py,out}` 추가 (기록자 계산 스크립트는 스크래치라 소멸).
EXPERIMENTS 행·DECISIONS 줄은 정정 없음. 메모: (d) 를 raw 중앙값으로 직접 계산하면 42 칸 중 최대 |차| 0.018 dB (§6.1 이 밝힌 반올림); 인용 arm p 값 4 칸은 scipy 언더플로 0 대 자체식 ≈ 1e-279 이하 (표기 차, §6.1 은 p 미전사); 새 18 쌍의 SNR@0.1 검열 복제 0 %; C6 runner 37.6 min 에는 첫 청크까지 준비 ≈ 9.5 min 포함; 예측 6 (`b* → SBL-loop`) 은 감사도 계산하지 않음; 동시 실행 목록은 감사 시점 (20:41 CDT) 에 살아 있던 프로세스만 보이므로 하한이며, 결과 값에 대한 영향은 판단하지 않는다.
