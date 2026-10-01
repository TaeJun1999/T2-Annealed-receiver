# 적대적 검토 — NEXT_EXPERIMENTS_SPARSE16e4 v1 초안 (Fable 5.1 서브에이전트, 2026-09-29 19:24 CDT = 09-30 09:24 KST)

- 대상: `conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md` (브랜치 sbl 1c5ffa6c), 코드 diff `git diff main -- conf/code` (arms.py dft_dict·SparsePrior·OMPSitePrior·build_our_arms(sparse), runner.py --sparse-arms, pair_baselines.py --add-baselines, sparse_tune.py, run_sparse_tune.sh, run_sparse16e4.sh), 튜닝 `results/sparse/tune_*.json` 5 개, `Demo/t2_route_a.py` run()·_sites, `code/d2.py`·`sv.py`·`mix3.py` 배열 기하, 틀 문서 STATIC16e4·ALD16e4·SUPP16e4.
- 검토자가 한 계산: 테스트 시행(0..2559)·개발 시행 어느 것도 쓰지 않았다. 사설 시드 `default_rng([77,1,2,3])` 의 D2 S2 채널 24 개 (C2, Tp=4, 파일럿 = `make_pilots`) 위에서 파일럿 전용 NMSE 만 계산 (스크립트: 스크래치패드 `sbl_check.py`; OMP_NUM_THREADS=2, GPU 숨김, BLER 없음, `run_sparse16e4.sh` 미실행). 새 arm 의 BLER 은 보지 않았다.

## 반드시

1. **OMP 의 L (그리고 SBL 의 n_em) 을 SNR 별로 고정하라 — 지금은 SNR 평균 한 값이 판정점에서 baseline 을 정확히 깎는다.** 위치: §1 하이퍼파라미터 행, §5 표, `sparse_tune.py` `pick`, `runner.py --sparse-arms`. 근거: 튜닝 JSON 자체의 SNR 별 최적 (ρ, L) — MIX3: −3 dB (8,3), 0 dB (8,4), +3 dB (8,8), ≥ 6 dB (·,24); SV8e: −3 dB (8,6), 0 dB (8,8), ≥ 3 dB (8,24); UMi28: −3 dB (8,4), 0 dB (8,8); S2·S2c: −3 dB L 3–4 → 15 dB L 24. 검토자 검사 (D2 S2, ρ 8, −3 dB): L=4 −6.09 dB, L=8 −4.52, L=24 **−3.14 = LS (−3.12)**; 15 dB: L=8 −19.57, L=24 −21.34, LS −21.39. 즉 SV8e·UMi28·MIX3 의 (8,24) 는 **OMP 가 아니라 24-atom LS** 이고, 파일럿 전용 arm 의 판정점(−3/0/+3 dB) 에서 3 dB 를 잃는다. SBL 도 같은 경향 (S2: −3 dB 최적 (4,100), 15 dB (4,200); MIX3 −3..+3 dB (2,25), 12–15 dB (4,200)). 선례: ALD16e4 §1 "멈춤 단계 = SNR 별 개발 평균 NMSE 최소 단계". 수정 (기존 튜닝 데이터로 충분, 재계산 없음): `sparse_tune.py` 에 `pick_per_snr` (같은 규칙을 SNR 별로: 최소 NMSE, 동률 → 작은 ρ → 작은 n_em/L) 를 기록; `runner.py --sparse-arms` 가 튜닝 JSON 경로(또는 `snr:rs,ne,ro,L;…`) 를 받아 `build_point(snr)` 에서 그 SNR 값을 고르고 `meta|sparse` 에 SNR 별 값을 적는다; §5 표를 데이터셋 × SNR 7 로 바꾼다; "격자 끝" 도 SNR 별로 표기.

2. **SBL 의 n_em 격자 끝(200) 은 수렴 미달이며 ρ 선택까지 왜곡한다 — γ 갱신을 MacKay 고정점으로 바꾸거나 n_em 격자를 더 넓혀라.** 위치: `arms.SparsePrior.gamma` (EM 갱신 `g = |mx|² + Σ_ii`), §1 "확장 뒤에도 끝이면 끝값 + 캐비엇, 더 확장하지 않는다", §5 D2 C2·D3 행. 근거: 튜닝 JSON S2 C2 ρ 8 열 −12.70/−12.79/−12.89/−13.10/**−13.54** (100→200 에서 0.44 dB 상승 중), ρ 4 열 100→200 0.12 dB; 검토자 검사 (15 dB, 24 채널): EM ρ 8 200 단계 −21.5 dB, 400 −22.5, 800 −23.0; **MacKay 고정점 (Tipping 2001 식 16, γ_i = |μ_i|²/(1 − Σ_ii/γ_i)) 25 단계 −23.2**; ρ 4: EM 200 −22.83 ≈ MacKay 25 −22.75. 수렴시키면 ρ 8 이 ρ 4 를 이긴다 — 현재 §5 의 "ρ 4, n_em 200" 은 단계 상한의 산물이다. 또 200 단계 EM 의 γ 는 전혀 희소하지 않다 (−3 dB: 512 개 중 γ < 1e-6 0 개, 상위 13.1·12.2·3.4·1.8…) — "희소 prior" 라기보다 저계수 Gaussian 에 가깝다. 수정 (택 1, 동결 전): (a) 갱신을 MacKay 고정점으로 바꾸고 n_em ∈ {10, 25, 50, 100} 으로 재튜닝 (25–50 단계에 수렴, 격자 끝 해소, SBL-loop 비용 4–8 배 감소); (b) EM 을 유지하면 n_em 을 {400, 800} 로 확장하고 §1 의 "더 확장하지 않는다" 를 ALD16e4 규칙("한 단계씩 최대 2 회") 으로 통일. 어느 쪽이든 −3 dB 에서는 EM 조기 종료가 0.15 dB 이득 (100 단계 −5.35 vs 수렴 −5.2) 이므로 n_em 은 정규화 손잡이로서 반드시 1 과 같이 SNR 별로 고른다. 이 변경 뒤 §0 두 번째 줄(튜닝 NMSE)·§3 예측을 다시 쓴다.

3. **수용 검사 "`meta|sparse` = §5 값" 이 코드에 없다.** 위치: §1 수용 검사 행, `code/eval_accept.py` (grep "sparse" 0 건), `run_sparse16e4.sh`. 수정: eval_accept 에 `--expect-meta KEY=VALUE` (반복) 를 추가해 모든 청크의 `meta|KEY` 문자열이 같은지 검사하고, 스크립트가 `--expect-meta "sparse=<json.dumps(sort_keys=True)>"` (반드시 1 뒤에는 SNR 별 문자열) 를 넘기게. 그렇지 않으면 §1 에서 그 문장을 빼고 pair_baselines 머리말에 `meta|sparse` 를 찍는 쪽으로 정직하게 적어라.

4. **CPU 비용 재산정과 실행 조건.** 위치: §1 비용 행 ("태그당 ≈ 0.5–2 h"), `run_sparse16e4.sh` (`--jobs` 없음 → `mp.Pool(min(cpu_count, tasks))`). 검토자 측정 (1 프로세스, 2 스레드): `SparsePrior.ep_site` N=32 ρ 4 n_em 200 = 0.083 s → SBL-loop 만 16 반복 × 2560 × 7 SNR = **6.6 CPU·h/데이터셋**; C6 (N=64) ρ 4 = 0.47 s → **37 CPU·h**, ρ 8 (M=4096) = 1.84 s → **146 CPU·h**; OMP ρ 8 L 24 = 0.043 s. 현재 부하 201 / 192 코어 (대형 수신기 작업 실행 중). 수정: §1 비용을 CPU·h 로 적고 `--jobs` 상한과 실행 순서(SEEDS3·HISNR 뒤) 를 명시; C6 의 ρ 후보를 비용까지 보고 동결 전에 정하라 (MacKay 로 바꾸면 4–8 배 감소).

5. **스모크 raw 가 워크트리에 남아 있다 — 삭제하고 기록하라.** 위치: `~/t2_wtSBL/conf/raw_spsmoke/D2_C2_S2_Nr8_T16_Tp4_dft_snr0_skip2560_n8.npz` (+ `results/gmm_fits_D2_spsmoke`). 새 3 arm 의 blk_err 가 들어 있으므로 파일이 있는 한 "BLER 수치는 보지 않았다" 는 검증 불가. 선례: ALD16e4 §4 "raw 삭제". 수정: 동결 전 삭제, §4 스모크 행에 "raw 삭제" 를 적는다.

6. **`run_sparse16e4.sh` 전제 검사에 "기존 출력 없음" 이 빠졌다.** 위치: 스크립트 머리 (STATIC 스크립트의 `ls pairB_ST*.txt && ABORT` 에 해당). 수정: `ls results/review_next/pairB_SP*.txt` 또는 `SP*_accept.txt` 가 있으면 ABORT (재실행은 사용자 승인); 부분 raw `raw_SP<suf>` 가 있으면 "resume" 임을 로그에 남긴다 (runner 는 끝난 청크를 건너뛴다).

## 권고

1. **OMP 오차 인지 변형 (OMPv-pilot)**: plug-in v = 1e-8 은 −3 dB 에서 NMSE −6 dB 짜리 추정을 정확하다고 믿는 수신기다. ALD16e4 가 ALDv 를 둔 것과 같은 이유로, 지지집합 LS 공분산 Σ_h = A_S (A_Sᴴ G A_S)⁻¹ A_Sᴴ (+ v I) 로 `Lam = Σ_h⁻¹ − G, eta = Σ_h⁻¹ ĥ − b` 를 돌려주는 변형을 함께 두면 (2 줄) "희소 모형" 과 "오차 인지" 가 분리된다. 아니면 §2 원고 문장에 "OMP 는 plug-in" 을 명시.
2. **SBL-loop 의 γ 웜스타트**: 지금은 외부 반복 16 번 모두 평탄 초기값에서 다시 시작한다. 이전 반복의 γ 에서 시작하는 것이 turbo-SBL 문헌의 표준이고 같은 n_em 으로 더 수렴한다. 단 prior 객체가 시행 간 공유되므로 `run()` 시작에서 리셋하는 훅이 필요 — 넣지 않으면 §2 에 "블록·반복마다 평탄 재시작" 을 적어라.
3. **OMP 의 잡음 기반 정지** (백색화 상관 최대값 < 임계 / 잔차 ≤ N σ²) 는 SNR 별 L 의 대안. 반드시 1 로 충분하나 원고에서 "고정 L (SNR 별 튜닝)" 이라고 적어라.
4. **off-grid (NOMP 등)**: D2 는 off-grid 각 L∈{3..8} 이라 NOMP (Mamandipoor 2016) 가 이 시나리오의 표준 강한 baseline 이다. 범위 밖으로 두더라도 §2 원고 문장을 "on-grid 2-D DFT 사전의 SBL·OMP" 로 한정. (검토자 검사: Nr=8 최악 on-grid 상관 ρ 4 0.975, ρ 8 0.994 → 격자 손실 자체는 작다.)
5. **예측 3 (OMP-pilot 셋 다 (i))·2 는 거의 예정**이다 (파일럿 전용 vs 루프 V1). ALD16e4 검토 #7 처럼 "정보 낮음" 표기. 정보 있는 쌍은 SBL-loop → V1 뿐이므로 ALD16e4 의 A1/A2 처럼 SBL-loop → V1 을 A1 로 두고 "주장은 A1 이 (i) 일 때만" 을 §1 에 명시하는 편이 낫다 (현재 (A) 도 셋 모두 (i) 를 요구하므로 논리는 같다; 문장 구조만).
6. **예측 추가**: ALD16e4 예측 5 처럼 "테스트 파일럿 전용 NMSE@1 (SBL-pilot·OMP-pilot) 이 §5 개발 NMSE 와 SNR 마다 ±0.5 dB" — 튜닝 스트림과 테스트 스트림의 분포 일치를 채점할 수 있는 유일한 항목.
7. `run_sparse16e4.sh` 의 `run_manifest.py --tag SP$SUF` 는 run|git raw 에는 불필요 (pair_baselines 는 run|git 이 있으면 매니페스트를 보지 않는다); 남기려면 그 json 도 커밋 대상임을 §4 에 적어라.
8. §1 "새 라벨 18 개" 와 다중성 문장 (보정 없음, 개수만) 을 SUPP16e4 §1 형식으로 한 칸 두어라 (현재는 판정 행 끝에 괄호).
9. `meta` 에 SBL 의 유효 희소도 (예: γ > 1e-3·max γ 개수의 중앙값) 를 보고 전용으로 남기면 원고에서 "희소" 라는 말을 방어할 수 있다.

## 확인 (문제 없음)

- **사전·기하**: 세 생성기 모두 반파장 ULA·단일 편파·omni (`d2.py:17`, `sv.py:13`, `mix3.py:14` PanelArray 1×N 기본 간격 0.5λ). 조향 e^{jπ n sinθ} 의 공간 주파수 sinθ/2 ∈ [−½,½] 는 격자 g/(ρn) (mod 1) 로 덮인다; 열 노름 1; vec 순서 vec(F_r X F_tᵀ) = (F_t ⊗ F_r) vec X 와 `np.kron(F(Nt), F(Nr))` 일치.
- **Woodbury EM**: (Γ⁻¹ + AᴴGA)⁻¹ = Γ − ΓAᴴ(I + GAΓAᴴ)⁻¹GAΓ, μ_x = ΓAᴴKb — 검토자 재검 M×M 대비 상대 오차 ≤ 9e-15 (ρ 2·4, 3 단계).
- **Gaussian 사이트**: `run()` 두 모드 모두 `P = Lam + G`, `hpost = Σ(eta + b)` 이므로 Lam = C⁻¹, eta = 0 은 CN(0, C) prior 의 정확한 사후 (C⁻¹ + G, (C⁻¹+G)⁻¹b). lam_min 무시는 무해 (Lam = C⁻¹ ≻ 0, 최소 고유값 ≈ 1/λ_max(C) ≈ 0.07 ≫ LAM_MIN 1e-6). eps = 1e-6 은 걸리지 않는다 (γ 최소 > 1e-6, eig(Cx) 최소 2.3e-3 @15 dB).
- **잡음 스케일**: G, b 는 `_sites` 에서 이미 1/σ² (파일럿 d = 1/σ²) — SBL 가능도·OMP 의 백색화 상관 |aᴴ(b−Gh)|²/(aᴴGa)·GLS 지지집합 해 모두 정합. 루프 모드의 데이터 열 d = 1/(σ² + τ·eh2) 도 b\* 와 같다.
- **초기값**: γ₀ = cbar·N/M; 튜닝 base cbar = 1 vs 실행 Cs cbar (D2 S2 표본 0.9987; SV·MIX3 는 코드에서 단위 전력 정규화) — 차이 무시 가능.
- **튜닝 스트림 독립**: `[20260930, TBID, PID, Nr, snr+100]` vs 시행 `[20260926, TBID, PID, Nr, T, Tp, snr+100]`·학습 `[20260926, TBID, which, PID, Nr]`; MIX3 `sample_vecs` 는 rng 로 Sionna 생성기를 시드 (사전 계산 풀 아님). 파일럿 행렬은 runner 와 같은 `make_pilots` 호출.
- **`--expect` 목록 = STATIC16e4 §6.1**: C2 12 개 (i) (V1-pilot (i) 2/3 포함), C6 V1-pilot (iv), SV8e b\*-scalar·gmm32·V1-pilot (iv) + `--expect-bstar (iv)`, D3·UMi28·MIX3 전부 (i); R0-pilot 은 `--r0 at1` 별칭 `R0-pilot@1` 로 대조. BS/KK/LL/SHA/ROLE 행은 `run_ald16e4.sh` DS 표와 동일.
- **16 개 셈**: b\* + 𝔅 12 + 새 3 = 16; 새 라벨 3 × 6 = 18; `--add-baselines` 는 BL 에 덧붙여 X\* 후보(−3 dB 실패 최소, 동률 이름순)에 자동 포함.
- **출처 혼합**: `pair_baselines --provenance manifest` 는 run|git 이 없는 raw 에만 매니페스트를 요구하고 run|git 이 있는 raw(새 SP) 는 "한 clean 커밋" 규칙으로 검사 (`pair_baselines.py:139-141`); extra raw 의 genie 4 키 = base 검사 있음 (:178-181).
- **수용**: `--arm … R5-genie` 부분집합 + genie 4 키 비트 동일 = PILOT/ALD16e4 선례와 같은 구조 (`runner.py` 점당 한 스트림, 안 만든 arm 은 스트림을 소비하지 않음).
- **CUDA 숨김**: 스크립트 전역 `CUDA_VISIBLE_DEVICES=`; 워커 스레드 1 (`runner.py:112`).
- **`pair_baselines` 기본 경로 불변**: `--add-baselines` 기본 [] → BL·miss 동일 (커밋 9b27cfd4 의 비트 동일 확인과 일치).
- **결과 후선택 경로**: §6 추가만, 라벨·X\*·R 규칙은 SUPP16e4 §1 인용, 예측은 튜닝 NMSE 열람 뒤 작성 공개. 반드시 5·6 외에 사후 선택 여지는 찾지 못했다.
