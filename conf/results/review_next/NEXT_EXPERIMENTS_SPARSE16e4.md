# NEXT_EXPERIMENTS_SPARSE16e4 — 정적 6 데이터셋에서 V1 대 **모델 기반 희소 baseline** (SBL·OMP) (사전 등록 v1 초안)

- 작성: 2026-09-29 19:09 CDT (= 09-30 09:09 KST) 초안 v1 (Opus 5.5). 적대적 검토(Fable 서브에이전트) → v2 → §5 (C6 튜닝) → 동결 커밋(`DECISIONS.md` 같은 줄). 커밋 뒤 §1~§3 을 바꾸지 않는다.
- 틀: `NEXT_EXPERIMENTS_STATIC16e4.md` (정적 6 데이터셋, 같은 raw·시행, `pair_baselines --provenance manifest`), `NEXT_EXPERIMENTS_ALD16e4.md` (개발 튜닝 → 동결 → 테스트, 격자 끝 규칙), `NEXT_EXPERIMENTS_SUPP16e4.md` §1 (표 B·라벨·X\*·R_X·문장 규칙).
- **작성 시점 공개**: 사용자 지시 2026-09-29 CDT ("빈 곳도 계획에 올려"; 빈 곳 2 = 무선 분야 리뷰어가 요구할 **희소 복원 baseline** 부재 — 09-27 요약 결정 대기 4번). 작성자는 정적 6 데이터셋의 기존 arm 결과(STATIC16e4 §6.1 포함)를 모두 봤다. 새 arm 3 개(SBL-loop, SBL-pilot, OMP-pilot)의 **BLER 은 한 번도 계산되지 않았다** — 스모크(D2 C2, 0 dB, 개발 시행 2560..2567, n = 8) 는 raw 구조·유한성만 확인했고 BLER 수치는 보지 않았다. 튜닝(§5)은 개발 NMSE 만 본다.
- 목적: "학습된 prior 가 **데이터 없이 쓰는 표준 희소 모형**보다 나은가". SBL 은 블록마다 가상 채널(오버샘플 2-D DFT) 위의 희소 분산을 EM 으로 추정하는 Gaussian prior 로, b\* 와 **같은 EP 수신기** ('gmm_site', exact_prior) 에 들어간다 — 달라지는 것은 prior 뿐이다.

---

## 0. 알고 있는 것 (판정에 쓰지 않는다)
- 정적 6 데이터셋의 13 baseline 표 B 는 STATIC16e4 §6.1 (규칙 고정 사후 계산): D2 C2·D3·UMi28·MIX3 에서 V1 이 13 개 전부보다 적게 실패; C6 은 V1-pilot (iv), SV8e 는 b\*·b\*-scalar·gmm32·V1-pilot (iv).
- 튜닝 NMSE (§5) — SBL 이 OMP 보다 1–2 dB 낮다 (C2 5 데이터셋). OMP 는 SV8e·UMi28·MIX3 에서 atom 상한 24 (N = 32 의 3/4) 를 골라 LS 에 가깝다.
- D2 의 경로 수 L ∈ {3..8} (off-grid 각도) — 희소 모형에 유리한 구조다. 38.901·SV8e 는 군집·확산 산란.

## 1. 고정되는 것
| 항목 | 값 |
|---|---|
| **새 arm (코드: 브랜치 sbl → 동결 커밋에서 main 병합)** | `SBL-loop` = `arms.SparsePrior(Cs, Nr, Nt, rho, n_em)` 를 `route_a(..., "gmm_site")` 에 (b\* 와 같은 수신기; 매 외부 반복마다 현재 (G, b) 로 γ 재추정); `SBL-pilot` = 같은 prior, `mode="pilot_only"` (파일럿만, 채널 믿음 고정); `OMP-pilot` = `arms.OMPSitePrior(Cs, Nr, Nt, rho, L)` pilot-only, plug-in v = 1e-8 (ALD-pilot 과 같은 방식). Cs = 같은 데이터셋의 full K32 적합 표본 공분산 (R2 와 같은 초기 상태; SBL 은 cbar·N 만 읽음). 사전 A = `arms.dft_dict(Nr, Nt, rho)`. SBL EM 은 N × N Woodbury 형 (M × M 식과 상대 오차 1e-13 확인) |
| **하이퍼파라미터** | 데이터셋마다 §5 의 튜닝값 (`code/sparse_tune.py`: 개발 채널 = 전용 스트림 default_rng([20260930, TBID, PID, Nr, SNR+100]), n = 256/SNR, 파일럿 전용 사후평균 NMSE 의 SNR 평균 dB 최소; 격자 ρ ∈ {1,2,4,8}, n_em ∈ {10,25,50,100,200}, L ∈ {1,2,3,4,6,8,12,16,24} — 첫 스모크가 ρ 4·n_em 100 끝에 걸려 **한 번 확장**; 확장 뒤에도 끝이면 끝값 + 캐비엇, 더 확장하지 않는다) |
| **실행 (테스트 시행, 데이터셋마다)** | `CUDA_VISIBLE_DEVICES= runner.py run --testbed D2 --prior <PR> --cell <CELL> --n 2560 --chunk 40 --ntrain 160000 --sparse-arms <rho_sbl,n_em,rho_omp,L> --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag SP<suf>` (fits 링크 `gmm_fits_D2_SP<suf>` → a1 적합; UMi28·MIX3 는 GPU 숨김 필수). 스크립트 `code/run_sparse16e4.sh` (main, 동결 커밋) |
| **수용 검사** | `eval_accept.py` (청크 {(40k,40)} × 7, meta ntrain·bstar·kron_K·ll_val, iters 16, **R5-genie 4 키가 base raw 와 비트 동일**) + `meta|sparse` = §5 값 |
| **판정 (데이터셋마다)** | `pair_baselines.py --base raw_<TAG> --pil raw_PIL<suf> --ald raw_ALD<suf> --est PIL<suf> --extra raw_SP<suf> --add-baselines SBL-loop SBL-pilot OMP-pilot --cell <CELL> --prior <PR> --r0 at1 --provenance manifest --expect-bstar <§0> --expect ...(STATIC16e4 §0 다섯 + 그 §6.1 의 새 8 arm 라벨)` → 표 B `X → V1`, X ∈ {SBL-loop, SBL-pilot, OMP-pilot} (**새 라벨 18 개**); 나머지 13 은 STATIC16e4 인용 (`--expect` 로 기계 대조). 라벨·X\*·R_X·가드는 SUPP16e4 §1 그대로 |
| **주 라벨** | D2 C2: 새 3 개가 모두 (i) → **(A) "V1 이 희소 baseline 3 개(SBL-loop, SBL-pilot, OMP-pilot) 전부보다 적게 실패"**; 그 밖 → (B) 개수 문장. 나머지 5 데이터셋 = 측정 라벨 |
| **"전부" 문장 (16 개)** | 원 b\* (i) **이고** 등록 baseline 15 개(𝔅 12 + 새 3) 모두 (i) **이고** (ii) 0 **이고** R_{X\*} CI 하한 > 0 (X\* 는 새 arm 포함 16 개 중 −3 dB 실패 최소) → "데이터셋 d 에서 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다" |
| 보고 전용 | 새 arm 의 R_X·절대 격차·SNR@0.1 격차, −3 dB 실패 수, NMSE@16 중앙값, `b* → SBL-loop` 표 B (GMM 대 희소 모형, 보고) |
| 비용 | CPU: 태그당 ≈ 0.5–2 h (SBL-loop 은 반복마다 EM; C6 가 가장 큼), 6 태그 순차 |

## 2. 라벨·문장
SUPP16e4 §2 그대로. 원고 문장 범위: 이 셀·예산·prior, 이 사전(오버샘플 2-D DFT)과 튜닝 규칙의 SBL·OMP.

## 3. 미리 적는 예측 (튜닝 NMSE 와 기존 arm 결과를 본 뒤; 새 arm BLER 은 미열람; 각 항목 적중/빗나감)
1. 주 라벨 D2 C2 = **(A)**.
2. D3·C6: 새 3 개 모두 (i) (데이터셋마다 한 항목).
3. UMi28·MIX3·SV8e: OMP-pilot → V1 은 셋 모두 (i) (한 항목).
4. UMi28·MIX3·SV8e: SBL-loop → V1 이 (i) 아닌 데이터셋 ≥ 1 (한 항목; 근거: 이 셋에서 V1 의 b\* 대비 우위가 작고 (R 0.06–0.14), 블록 적응 SBL 이 GMM 보다 나을 수 있다).
5. 새 18 라벨 중 (ii) ≤ 1 (한 항목).
6. 보고 전용 `b* → SBL-loop`: D2 C2 에서 b\* 가 SBL-loop 보다 적게 실패 — (ii) (한 항목; GMM 이 D2 분포를 학습).
7. 빗나갈 경로: 수용·무결성 실패 → 그 데이터셋 무효; `--expect` 불일치 → 드리프트.

## 4. 선행 작업
| 항목 | 상태 |
|---|---|
| 코드 (브랜치 sbl): arms.dft_dict·SparsePrior·OMPSitePrior + build_our_arms(sparse=…); runner `--sparse-arms` (meta|sparse 기록); pair_baselines `--add-baselines`; sparse_tune.py | 구현. 스모크: runner D2 C2 0 dB 개발 n = 8 — 세 arm raw 생성·유한·meta 기록; SBL Woodbury = M × M (1e-13); pair_baselines 기본 경로 = STATIC16e4 B16e4k 출력 비트 동일 |
| `run_sparse16e4.sh` (fits 링크, 전제 검사, 실행 → 수용 → pair_baselines; `--expect` 로 STATIC16e4 의 13 라벨 대조) | 작성 (C6 행의 `--sparse-arms` 는 튜닝 뒤 채움; TBD 면 그 데이터셋 ABORT) |
| 튜닝 6 데이터셋 | C2 5 완료, C6 진행 중 (§5) |
| 적대적 검토 → v2 → §5 → 동결 (sbl → main 병합) → 실행 (CPU 순서: SEEDS3 BLER, HISNR 뒤) | 대기 |

## 5. 평가 전 고정 기록 (튜닝; 개발 NMSE 만)
| 데이터셋 | SBL (ρ, n_em) · 평균 NMSE dB · 격자 끝 | OMP (ρ, L) · 평균 NMSE dB · 격자 끝 | `--sparse-arms` |
|---|---|---|---|
| D2 C2 (S2) | 4, 200 · −14.19 · n_em | 8, 8 · −12.59 · ρ | 4,200,8,8 |
| D3 (S2c) | 4, 200 · −14.43 · n_em | 8, 8 · −12.80 · ρ | 4,200,8,8 |
| SV8e | 2, 25 · −13.02 · — | 8, 24 · −11.95 · ρ, L | 2,25,8,24 |
| UMi28 | 2, 25 · −13.58 · — | 8, 24 · −12.03 · ρ, L | 2,25,8,24 |
| MIX3 | 2, 50 · −13.89 · — | 8, 24 · −12.02 · ρ, L | 2,50,8,24 |
| D2 C6 (S2) | (튜닝 중) | | |

튜닝 파일 `results/sparse/tune_<prior>_<cell>.json` (브랜치 sbl, 동결 커밋에 포함).

## 6. 결과 (이 절은 추가만 한다)
