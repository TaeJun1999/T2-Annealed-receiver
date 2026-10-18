# E3′ SBL32 코드 작성·검증 보고

기록: 2026-10-17 11:53:42 CDT (`date` 출력). 작업 HEAD `64b2912f8ae6c4b9bc9ac373d2e3a6b83c4e4c08` + 미커밋 변경.
작업 위치 `/home/HTJ/t2_wtE3`만 쓰기. 커밋·삭제·push 없음. main과 다른 worktree는 읽기만.

## 변경 사항

- `conf/code/arms.py`: `SparsePrior(..., warm=False)` 추가. warm에서만 객체별 마지막 γ와 CURRENT_TRIAL을 저장한다. 같은 명시적 시행이면 이어서 n_em 갱신, 다른 시행이면 기존 평탄값에서 시작한다. CURRENT_TRIAL=None이면 호출마다 평탄 시작한다. SBL-loop/SBL-pilot은 별도 prior 객체다.
- `conf/code/runner.py`: `--sparse-arms RHO_SBL,N_EM,RHO_OMP,L[,WARM]`. 네 값·다섯째 0은 기존 dict 그대로이고, 1일 때만 `"warm": true`를 넣어 raw의 `meta|sparse`에 남긴다. `--sparse-file` 적재·해석 경로는 수정하지 않았다.
- `conf/code/sbl_probe.py`: cold 9개 설정의 단일 개발 packet 비용·5회 gamma 한 단계 시간·fresh-process 최대 RSS·이상적 병렬 시간 추정. 복호 결과를 출력·저장하지 않는다. 각 행의 JSON도 완료 즉시 보존한다.
- 이 폴더의 `prepare_inputs.py`, `regression_sbl32.py`, `verify_stream_sbl32.py`, `finalize_report.py`, `run_checks.sh`, `run_final.sh`: 입력 복사·회귀·시행 스트림 확인·보고 자동화. `docs/EXPERIMENTS.md`에는 이 worktree의 코드 검증 행만 추가한다.

**cold 비트 동일의 이유:** 기본 경로에서 초기 γ 생성식, MacKay/EM 반복문의 연산·순서, `ep_site`의 행렬 연산을 그대로 두었다. warm일 때만 다른 시작값을 택하고 상태를 복사한다. γ 경로를 공용 함수로 재작성하지 않았다. 근거는 아래의 저장 raw 바이트 비교다.

## 실행으로 확인한 것

실행은 tmux `e3_sbl32_checks2`, `e3_sbl32_final`의 스크립트 파일에서 순차 수행했다.
공통 환경: `CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1`; Python `/home/HTJ/miniforge3/envs/torch/bin/python`; `taskset -c 0-1`. NumPy·SciPy의 실제 로드된 OpenBLAS getter는 각각 1을 반환했다 (`regression.out:3`). 채널 생성은 기존 Sionna/torch CPU 경로다. 최종 설정의 `/proc` 환경·affinity·스레드별 CPU 시간·nvidia-smi 조회도 `resource_snapshot.txt`에 보존했다. 보조 스레드 2개의 관측 CPU 누적 시간은 0이었다.

명령:
```sh
bash conf/results/review_next/sbl32/run_checks.sh
taskset -c 0-1 /home/HTJ/miniforge3/envs/torch/bin/python conf/results/review_next/sbl32/verify_stream_sbl32.py
taskset -c 0-1 /home/HTJ/miniforge3/envs/torch/bin/python conf/results/review_next/sbl32/finalize_report.py
```
각 명령에는 위 공통 환경이 적용된다. 회귀의 정확한 runner 명령 2개는 `regression.out`의 COMMAND 행과 `raw_regression.json.commands`에 있다.

- **cold raw 회귀:** `conf/raw_SPU28/D2_C2_UMi28_Nr8_T16_Tp4_eig_snr-3_skip0_n40.npz` (원 run git 02dafa1c), UMi28 C2 8×4, −3 dB, trial 0..39, ntrain=160000, ρ_SBL=8, n_em=3, ρ_OMP=16, L=3, beta=.7, tin=5, 16회, Stage C 미사용. 원 meta/run 값을 읽어 네 값과 다섯째 0 두 경로로 SBL-loop만 다시 실행했다. 모든 KEYS_RAW 7개 × 두 경로 = **14/14 바이트 동일**, 각 shape=(40,16), cold `meta|sparse` 문자열 동일, 예외 없음 (`regression.out`, `raw_regression.json`). 원 raw와 fit은 수정하지 않았다. 이는 **청크 수신기 재실행 비교**이며 학습부터 재실행한 것이 아니다.
- **warm 단위:** MacKay·EM × ρ=1,2,4, n_em=3, 동일 (G,b) 4회 호출과 γ_path 12단계 비교; 시행 전환 site 초기화; 비활성 객체의 임의 호출 순서·이전 HEAD 구현 비교; CURRENT_TRIAL 미지정 보호 = **72 cases PASS**. CLI별 build/meta 3개, 객체 상태 분리, sparse-file meta, 잘못된 WARM/개수 거부도 PASS.
- **기존 arms 회귀:** C2, C3, C4, C5, M1, M1b, M2, M2b, M4 **9/9 PASS**. M2b 잔차 1.2832790385886028e-13 ≤ 1e-10; 나머지 정확성 잔차 0 (`regression.out`). conf/code 테스트 파일에서 전용 SparsePrior 회귀는 찾지 못했다. 이 기존 검사는 독립 seed의 D1 합성 단위 검사이며 새 runner test 점 평가는 아니다.
- **프로브 배선·스트림:** 실제 runner.build_point의 sparse SBL-loop와 직접 생성한 객체·배선·prior 값이 같다. runner의 R5-genie.transmit을 이용한 원 시행 생성 루프와 프로브의 개발 trial 2560 (H,u,perm,Y)이 바이트 동일 (`verify_stream_sbl32.json`, `.out`). 이 확인은 receiver.run을 호출하지 않는다. 0..2559는 스트림 위치를 맞추기 위해 생성만 하고 복호/평가하지 않는다.
- **범위 무결성:** main의 HEAD·index SHA-256·arms.py·runner.py·잠긴 Demo 3파일은 시작/끝 동일. worktree Demo의 git status도 비어 있음 (`final_audit.json`). Demo lock ID `3b5c0a375509`. `git diff --check`와 수정·추가 Python의 메모리상 compile 통과.

주 로그: `conf/logs/sbl32_checks2.out`, `.err`, `conf/logs/sbl32_final.out`, `.err`.
첫 실행은 threadpoolctl 미설치로 수신기 평가 전에 중단됐다 (`conf/logs/sbl32_checks.err`). 외부 파일/환경에 패키지를 설치하지 않고 로드된 BLAS getter 확인으로 바꾼 뒤 위 검사가 통과했다. 그 실패 기록도 보존했다.

## 프로브 실측과 계산상 추정

UMi28 C9 32×4, T=16, Tp=4, QPSK, 0 dB, 개발 **trial 2560 한 블록/설정**, cold, 외부 16회. RNG seed tuple `[20260926, 2, 8, 32, 16, 4, 100]`. 모든 행은 별도 프로세스다. 한 단계 시간은 해당 receiver의 첫 G(128×128), b(128)에서 `gamma(n_em=1)` 5회 중앙값이며 평탄 초기화와 I 할당을 포함한다. 블록 시간은 rx.run 벽시계로, 최초 G/b 복사 및 호출 계수 계측을 포함한다. 초기화/2560개 skip 스트림 생성/파일 I/O는 제외한다.

| rho | n_em | gamma step (s, median/5) | block (s) | ep_site calls | max RSS (MiB) | W96 (h) | W119 (h) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 3 | 0.022855 | 4.765 | 16 | 881.8 | 0.247 | 0.199 |
| 4 | 10 | 0.016460 | 12.398 | 16 | 878.4 | 0.643 | 0.519 |
| 4 | 25 | 0.026556 | 39.051 | 16 | 878.0 | 2.025 | 1.633 |
| 8 | 3 | 0.069902 | 33.897 | 16 | 947.9 | 1.758 | 1.418 |
| 8 | 10 | 0.086128 | 43.338 | 16 | 948.5 | 2.247 | 1.813 |
| 8 | 25 | 0.077095 | 122.003 | 16 | 947.1 | 6.326 | 5.103 |
| 16 | 3 | 1.430304 | 124.065 | 16 | 1176.0 | 6.433 | 5.190 |
| 16 | 10 | 0.324233 | 295.339 | 16 | 1174.0 | 15.314 | 12.354 |
| 16 | 25 | 2.973147 | 774.184 | 16 | 1177.0 | 40.143 | 32.384 |

출처: `probe_U28NR32.json.rows`, `probe_U28NR32_rho*_em*.json` (5개 시간 표본 포함), `probe.out`. RSS는 resource.getrusage(RUSAGE_SELF).ru_maxrss (KiB)로, imports/Sionna/블록/단계 측정 전체 프로세스의 high-water다. 필요한 Chat과 SBL-loop만 생성한 프로세스의 값이며, runner.build_point가 arm 선택 전에 만드는 미사용 GMM·다른 arm 객체의 메모리는 포함하지 않는다. 복호 결과/BLER/블록 성공·실패 값은 이 산출물에 없다.

**계산상 추정:** W96·W119 열은 `block_sec × 17920 / W / 3600`. 실제 7 SNR·96/119 워커 실행은 하지 않았다. 한 개발 블록과 현재 공유 서버 부하의 실측이므로 SNR별 변화·메모리 대역폭 경쟁·병렬 효율·추가 초기화와 skip 재생성 비용을 포함한 완료 시각 예측으로 해석할 수 없다. gamma 단계는 모든 행에서 n_em=1로 재므로 같은 rho의 행 간 단계 시간 차이를 n_em의 효과로 해석하지 않는다. 5회 표본에도 변동이 있으며 원표본은 JSON에 보존했다. 통계적 BLER 추정이나 신뢰구간은 산출하지 않았다.

## 복사 입력과 SHA-256

첫 3개는 main에서 같은 상대 경로로 `cp -L` 복사했다. 마지막 2개는 그 worktree의 8×4 fit에서 회귀 tag routing용으로 `cp -L` 추가 복사했다. 모두 일반 파일이며 링크가 아니다. 전체 source/destination/바이트 수/sha는 `input_manifest.json.copies`에 있다.

| worktree 내 경로 | SHA-256 |
|---|---|
| `conf/raw_SPU28/D2_C2_UMi28_Nr8_T16_Tp4_eig_snr-3_skip0_n40.npz` | `e8aff0d8df0d00455c5696b0d75c5bc591cb01aa1a493959f870c37667033a53` |
| `conf/results/gmm_fits_D2_SPU28/fit_UMi28_Nr8_fullK32_n160000.npz` | `c0261395e7238650a447cbbcc5a061c4161bd9fb23f118600dcd3541938f3194` |
| `conf/results/gmm_fits_D2_U28NR32GCAPchk/fit_UMi28_Nr32_fullK32_n160000.npz` | `d572e0ac63013a96042a148aa1fceaa6662710ddfdbcfb4a4dd051271704e215` |
| `conf/results/gmm_fits_D2_SBL32REG4/fit_UMi28_Nr8_fullK32_n160000.npz` | `c0261395e7238650a447cbbcc5a061c4161bd9fb23f118600dcd3541938f3194` |
| `conf/results/gmm_fits_D2_SBL32REG5OFF/fit_UMi28_Nr8_fullK32_n160000.npz` | `c0261395e7238650a447cbbcc5a061c4161bd9fb23f118600dcd3541938f3194` |

## 남은 불확실성·미실시

- warm의 실제 32×4 packet 성능/BLER·cold/warm 후보 선택·full test 평가·병렬 속도 검증은 하지 않았다. 개발 튜닝은 별도 등록 뒤 수행할 작업이다.
- 프로브에서 SBL-pilot·OMP-pilot의 32×4 receiver.run은 호출하지 않았다. stream 배선 검사에서는 build_point가 이 객체들을 만들기만 한다. OMP 코드는 바꾸지 않았다.
- 회귀는 지정 청크와 위 단위 사례의 범위다. 모든 기존 raw를 재평가한 것은 아니다. 검사한 cold 계산에는 변화가 없어 기존 실행을 무효/재평가 대상으로 바꿀 사유는 확인되지 않았다.
- Claude의 독립 검토, 측정 도구의 독립 정답 사례 확인·사용자 잠금, 커밋은 아직 수행하지 않았다. 새로운 등록/결과 선택 규칙·DECISIONS·RESULTS·원고·그림은 수정하지 않았다.
