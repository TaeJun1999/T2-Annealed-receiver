# NEXT_EXPERIMENTS_E5QAM16 — 동결 prior 의 16-QAM 재사용: UMi28 C2 8×4 (주검증, U28QAM16) · D2 C2 8×4 (보조, D2QAM16) — 사전 등록 v2.1

작성 2026-10-17 CDT (Opus 5.5). 사용자 과제 `conf/results/review_next/prompts/PROMPT_SERVER_QAM16.md` (웹 채팅 2026-10-16 CDT; 공통 규칙 `gcap/PROMPT_SERVER_COMMON.md`). 이 문서의 §0–§4 와 SNR 격자 규칙 (§1.2) 은 **개발 BLER 을 보기 전에** 브랜치 `e5-qam16` 에 커밋한다 (main 은 U28NR32GCAP 실행 중이라 커밋 금지). 실행 커밋 = §5 를 더하고 `e5-qam16` 을 main 에 병합한 커밋.

### v2 → v2.1 (2026-10-18 14:15 CDT, test 미사용)
- Codex 교차 검토 (gpt-6-astra · max, 사용자 승인; `reviews/20261019-035934-prompt_pretest_sbl32_e5_gcap6.md` 묶음 B) 결함 1 수용 — §1.4 머리의 실행 명령에 필수 환경변수 `E5_CPUS` (run_e5.sh:26) 를 넣고 §5 에 시작 명령을 적음. 확인 필요 1 (D2 시작 규칙을 실제 UMi 종료 시각에) 은 §5 에 적음. 규칙·수치 변경 없음.

### v1 → v2 (개발 BLER 미열람)
- 적대적 검토 (Fable 5.1, `prereg_reviews_2026-10-17/review_E5QAM16.md`): MUST 2 · SHOULD 9 · NIT 5 — 전부 반영. M1 16-QAM 의 시행 스트림은 trial 1 부터 QPSK 와 H·잡음이 다르다 (§1.4 '같은 시행', §1.3); M2 수용 명령·고정 수치 (§1.1, §1.4). S1–S3 격자 스크립트 (meta 검사, 비단조·경계 문장, sha), S4 `b* → V1-pilot` 계산 경로, S5 스모크 태그, S6 ν_q 명령·예측 4 채점, S7 ckpt 절대경로·전체 sha, S8 D2 시작 규칙, S9 예측 3·라벨 매핑.
- 코드 교차 검토 (Codex gpt-6-astra · max, `reviews/20261018-040035-prompt_qam16_code.md`): runner 결함 2 (재개 때 변조 혼합, smoke 성공 판정) — Codex 가 고침 (§4); 같은 검토가 M1 을 독립적으로 실측.

## 0. 알고 있는 것 (판정에 쓰지 않는다)

- QPSK 기록 (RESULTS §10.1, 판정 태그 `_best`): UMi28 C2 (`U28B16e4`) 판정점 +3/+6/+9 dB, 표 B `b* → V1` 161:73 (i), SNR@0.1 격차 +0.60 dB [+0.33, +0.87] (UMi 세 배열 가운데 가장 작다); SNR@0.1 b\* 5.73, V1 5.13, genie 0.59 dB. D2 C2 헤드라인 (`B16e4k`) −3/0/+3 dB, 454:78 (i), +1.41 dB [+1.22, +1.64].
- 16-QAM 은 K_b = 4 · 12 · 4 / 2 − 6 = 90 (QPSK 42). payload 가 달라 QPSK 와의 차이를 순수한 변조 효과로 읽지 않는다. 학습 prior 와 GMM 은 둘 다 채널 표본만으로 학습했으므로 변조와 독립 — 이 실험은 diffusion 만의 장점을 보이는 실험이 아니다.
- 시행 스트림: runner 는 한 스트림에서 시행마다 H → 정보 비트 u (K 개) → perm → 잡음 순으로 뽑는다. K 가 42 → 90 이면 trial 0 의 H 만 QPSK 와 같고 trial 1 부터 H·잡음이 다르다 (Codex 실측: REPORT §Seed, 교차 검토). 따라서 16-QAM 실험은 QPSK raw 와 시행 단위로 짝을 이루지 않는다.
- 개발 시행 사용 (전체 홈 조사, 검토 N1): UMi28 C2 raw 는 2560..3839 와 10000..30479 (보강), D2 C2 는 ≤ 5119 와 10000.. (보강); ALD 개발 입력 2560..3071; Codex 16-QAM 스모크 2560..2563. **5120..5519 는 두 셀 어디서도 쓰이지 않았다.**
- 코드 (브랜치 `e5-qam16` 커밋 fb5e365d + 결함 수정 커밋 (§4); Codex 작성, Claude 검토, golden PASS): `runner.py --mod qpsk|16qam`; QPSK 기본 경로는 기존 raw 와 392 배열 바이트 동일; 16-QAM 에서 BiG-AMP · SC-VAMP (QPSK 도우미) 는 만들지 않는다; 기존 `runner.py analysis` 는 16-QAM raw 를 거부한다 — 분석은 §1.4 의 전용 스크립트로. worktree 의 추적되지 않은 `conf/raw_U28B16e4/` · `conf/results/gmm_fits_D2_U28B16e4/` 등 (Codex 회귀 입력 복사본) 은 지우지 않는다.

## 1. 고정되는 것

### 1.1 셀·모델·arm (기존 raw meta 와 대조한 값)

| | UMi28 C2 (주검증) | D2 C2 (보조) |
|---|---|---|
| 인자 | `--prior UMi28 --cell C2` (송신 상관 고유벡터 파일럿) | `--prior S2 --cell C2` (DFT 파일럿) |
| V1 체크포인트 (절대경로) | `/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt` sha256 `6f3a1b9490864af11fc07b2babe665825f5f56d93a98e39414fac29598463d1c`, role best (epoch 379), stagec id `sha256[:16]=6f3a1b9490864af1 epoch=379 best_epoch=379 role=best 8x4` | `/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt` sha256 `4443921ce8d5c4a11c7cda879a53a66436f43bd76864734a3e6203cfb4b82f29`, role legacy-last (epoch 1784, best 1764 — best 가중치 미보존) |
| fits 폴더 (바이트 복사본, 링크 아님) | `results/gmm_fits_D2_U28QAM16` = `gmm_fits_D2_U28B16e4` 의 24 파일 (병합 15 + 후보 `.k0r*` 9; `load_fits` 는 병합 이름만 읽는다) | `results/gmm_fits_D2_D2QAM16` = `gmm_fits_D2_B16e4k` 의 24 파일 (Nr8 13 + Nr4 11; 원본은 `gmm_fits_D2_n16e4` · `gmm_fits_D2_K1024n160000` 로의 링크 → `cp -L`) |
| b\* (ll_val argmax, 기존과 같음) | kron K 4096, sha256 `74d22f332726203f512ddfb4289d59ad10bb3f4f67c9ef7cb275821a32aa01f8`, ll_val **5.797910431000217**, em_sec 9133.61854147911 — 격자 끝, 한정어 유지 | kron K 1024, sha256 `bf796b84037e1b3790ed5a6d7917ea2a79f2bee4a9f155f0d3385d856c950997`, ll_val **−11.459169831224418**, em_sec 107957.18832826614 |
| R2 의 Chat (fullK32) | sha256 `c0261395e7238650a447cbbcc5a061c4161bd9fb23f118600dcd3541938f3194` | sha256 `d4601650a888b4b355565a9010cf0a23499a3e92505e657e2cd79a1c152359f3` |

- 변조: `--mod 16qam` — 정규화 Gray 16-QAM (평균 심볼 에너지 1, 블록마다 재정규화 없음), K_b 90, 같은 셀의 모든 arm 이 같은 90 비트 packet. T 16, T_p 4, 채널 정규화, SNR 정의 (σ² = 10^(−SNR/10)) 는 QPSK 와 같다. 외부 반복 16, CPU complex128.
- arm: V1 (`M-ours-dscore-C-V1`, `--stagec-ckpt`), b\* (`M-ours-bstar`), R2 (`R2-ours-G`), R5-genie, V1-pilot (`--pilot-arms`). 실행은 `--pilot-arms --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie V1-pilot`.

### 1.2 SNR 격자 (개발; b\* 의 BLER 만 본다 — 이 규칙은 개발 BLER 을 보기 전에 커밋한다)

1. 셀마다 초기 후보 격자 G0 = {3, 6, 9, 12, 15, 18, 21} dB. 개발 시행 **5120..5439 (n = 320)** 에서 **b\* 만** (`--arm M-ours-bstar`) 돌린다 (`qam16/run_grid.sh`, 태그 `U28QAM16g` · `D2QAM16g`, fits = §1.1 의 바이트 복사본 · sha 대조).
2. **안쪽 조건**: b\* 의 BLER@16 (실패 / 320; raise 시행 = 실패) 이 G0 의 첫 점에서 > 0.1 이고 마지막 점에서 < 0.1 이면 G0 를 쓴다 (BLER 이 정확히 0.1 이면 '안쪽 아님').
3. 아니면 **한 번만** 3 dB 옮긴다: 첫 점에서 이미 ≤ 0.1 이면 아래로 (G0 − 3 = {0, …, 18}), 마지막 점에서 ≥ 0.1 이면 위로 (G0 + 3 = {6, …, 24}); 옮긴 격자의 새 점 하나 (0 또는 24 dB) 를 같은 개발 시행에서 b\* 로 돌려 기록한다. 옮긴 뒤에는 안쪽 조건과 무관하게 그 격자를 쓴다 (다시 옮기지 않는다); 안쪽 조건이 여전히 깨지면 그 사실을 적고 판정은 §2 의 자동 규칙 (power guard) 에 맡긴다. 둘 다 깨지면 (BLER(+3) ≤ 0.1 이면서 BLER(+21) ≥ 0.1 — b\* 비단조) 옮기지 않고 G0 를 쓰며 그 사실을 적는다.
4. 판정점은 test 데이터에서 기존 자동 규칙 (앵커 b\*, |log10(BLER/0.1)| 최소, BLER ∈ [0.005, 0.9]) 으로 정한다 — 격자 선택과 독립.
5. 계산은 `qam16/select_grid.py <tag>` (이 커밋; 무결성: SNR 마다 10 시행 청크 32 개로 5120..5439, (10, 16) 모양 · `run|iters` 16 · `run|n` 10 · `run|skip`/`run|snr` = 파일 이름, 모든 청크 `run|git` 하나, meta modulation 16qam · payload_bits 90 · protocol E5-qam16-v1 · bstar kron · kron_K · `ll_val|kron` = §1.1; 출력 `qam16/select_grid_<셀>.out`).

### 1.3 질의 범위 진단 (개발, 보고 전용)

- 고른 격자의 7 SNR 에서 개발 시행 5440..5479 (n = 40) 로 V1 의 질의 잡음 ν_q 를 반복별로 기록하고, 체크포인트의 학습 σ 범위 (sigma_tag 의 동결 격자) 밖 비율을 반복·SNR 별로 낸다. 명령 (UMi): `CUDA_VISIBLE_DEVICES= taskset -c <한 쌍> python code/diag_sigma_coverage.py --mod 16qam --cell C2 --prior UMi28 --tag U28QAM16g --ntrain 160000 --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt --snr <격자 7 값> --skip0 5440 --n 40 --out results/review_next/qam16/coverage_U28QAM16_16qam.npz`; QPSK 비교 = 같은 인자에 `--mod qpsk`, `--out …_qpsk.npz` (같은 시행 **번호**, 채널 실현은 다르다 — §0). D2 는 `--prior S2 --tag D2QAM16g --stagec-ckpt /home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt`. ν_q 만 저장하고 BLER 은 내지 않는다. 학습 범위는 percentile 로 정했으므로 일부 벗어남은 실패나 재학습 사유가 아니다. 재학습하지 않는다.

### 1.4 test 평가 (셀마다; UMi 먼저, D2 다음; 실행 = main 병합 커밋에서 `E5_CPUS=<허용 CPU 목록> bash code/run_e5.sh U28|D2 [--resume]`, tmux — `E5_CPUS` 가 없으면 스크립트가 시작 전에 멈춘다; 이 실행의 목록은 §5)

| 항목 | 고정 값 |
|---|---|
| 주 실행 | `CUDA_VISIBLE_DEVICES= taskset -c <허용 CPU> python code/runner.py run --testbed D2 --prior <UMi28|S2> --cell C2 --ntrain 160000 --stagec-ckpt <§1.1 절대경로> --pilot-arms --mod 16qam --chunk 40 --n 2560 --snr <§5 격자> --arm M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R5-genie V1-pilot --worker-gb <G> --tag <U28QAM16|D2QAM16>` — 7 SNR × test 0..2559 = 448 청크. fits 폴더 = §1.1 (스크립트가 sha 대조) |
| CPU · 메모리 | 워커 = min(허용 스레드, 448, ⌊0.8·MemAvailable / G⌋). G·시간: **스모크** = 태그 `U28QAM16dev` (`D2QAM16dev`), fits `gmm_fits_D2_U28QAM16dev` = test 폴더의 바이트 복사본 (cmp), 격자 4 번째 SNR, 다섯 arm, `--skip0 5480 --n 40 --chunk 40`, 1 스레드 → 실행 트리 최대 RSS × 1.05 를 0.5 GB 단위로 올림 = G, 청크 시간 t → 총시간 ≈ ⌈448 / 워커⌉ × t (§5). 스모크 raw 의 BLER 은 열지 않는다 (runner 는 16-QAM 에서 BLER 을 찍지 않는다). 시작 전 다른 실행 (GCAP · SBL32) 과 CPU 합계를 확인 — 사용자 상한을 넘으면 순서를 묻는다 |
| 같은 시행 | 같은 run 안의 다섯 arm 은 같은 (H, u, perm, Y) 를 본다 (runner 가 시행마다 transmit 을 한 번 호출). 16-QAM 시행 스트림은 QPSK 와 seed 만 같고 trial 1 부터 H·잡음이 다르다 (§0). test 집합 = 16-QAM 스트림의 trial 0..2559 (번호 기준; 공통 규칙의 '기존 arm 과 같은 시행' 은 이 실험에서 성립하지 않으며 QPSK raw 와 비트 대조하지 않는다). 개발 (5120..5519) / test (0..2559) 분리는 번호 기준이고, 16-QAM 스트림의 어느 번호도 BLER 로 열람된 적이 없다 |
| 수용 | ① `python code/eval_accept.py --tag U28QAM16:best:6f3a1b9490864af1:C2 --prior UMi28 --ntrain 160000 --kron-K 4096 --ll-val 5.797910431000217 --points C2:<§5 격자 7 값> --chunk 40 --n 2560` (D2: `--tag D2QAM16:legacy-last:4443921ce8d5c4a1:C2 --prior S2 --kron-K 1024 --ll-val -11.459169831224418`). `--ref-raw` 는 쓰지 않는다 (§0). ② `run_e5.sh` 의 추가 검사 (448 청크 전부): `run|git` = HEAD (+dirty 없음), meta modulation 16qam · payload_bits 90 · protocol E5-qam16-v1, 다섯 arm × `common.KEYS_RAW` 가 모두 (40, 16). ①·② 모두 OK 일 때만 분석 표를 결과로 쓴다 |
| 분석 | `code/e5_compare.py --raw raw_<tag> --cell C2 --prior <…> --out results/review_next/qam16/compare_<tag>.txt`: `analysis.table_B` 의 `b* → V1` (판정점 = 앵커 b\* 자동, 판정점별 exact 양측 부호검정 p < .05, 2/3 규칙, power guard, SNR@0.1 격차 90 % paired bootstrap B 2000); ΣF (b\*, V1, genie; 판정점 합), R = (F_b\* − F_V1)/(F_b\* − F_genie) [90 % paired bootstrap, `recovery_ci` 의 함수, 판정점은 table_B 의 것]; 7 SNR × 다섯 arm BLER@16 표 (실패 / 2560; raise = 실패). 보고 전용 `b* → V1-pilot` (라벨 없음): `analysis.table_B` 는 V1-pilot 을 만들지 못하므로 e5_compare 가 같은 함수 (`decision_points` 앵커 b\*, 판정점별 부호검정 `paired`, SNR@0.1 격차 `gain` B 2000 seed 20260925) 를 직접 불러 같은 형식으로 낸다 |
| 끝 표시 | 로그 `logs/run_e5.log`, `E5_DONE <셀> ok=<n> fail=<n>` |

### 1.5 예외·중단

- runner 비정상 종료 · 메모리 초과: 같은 HEAD 에서 `--resume` (`--mod 16qam` 포함 — 코드가 변조 혼합을 막는다). 수용 실패 → 표를 결과로 쓰지 않고 사용자에게 보고.
- 판정하지 못함 ((iii)·(iv)) 도 완료된 결과. SNR 점·표본을 늘리지 않는다. 결과를 본 뒤 셀·격자를 바꾸지 않는다.
- **D2 시작 규칙**: D2 test 는 UMi 결과와 무관하게, (UMi 종료 시각 + §5 의 D2 추정 총시간) ≤ 2026-10-24 06:00 CDT (원고 반영 마감 10-24 18:00 CDT 전 감사·전사 12 h) 일 때만 시작한다; 아니면 시작하지 않고 그 추정치를 기록한다.
- 실행 중 다른 세션이 main 에 커밋하면 `--resume` 의 run|git 검사가 막는다 → 사용자에게 알린다. 개발 실행이 도는 동안 `e5-qam16` 에 커밋하지 않는다 (runner 는 워커가 첫 청크를 쓸 때 HEAD 를 읽는다).

### 1.6 하지 않는 것

다른 baseline 의 16-QAM 대응, 재학습, 체크포인트를 다른 채널 모델로 옮기는 평가, 결과를 본 뒤의 셀·격자 변경, QPSK 결과와의 차이를 변조 효과로 읽는 문장, QPSK raw 와의 시행 단위 짝 비교.

## 2. 라벨·문장

### 2.1 UMi28 (주검증, E5 의 유일한 primary 비교) — 표 B `b* → V1`
라벨 = `analysis.table_B` 의 문자열에 묶는다 (GCAP §2.1 과 같다): POWERED 이고 "second arm fewer failures" 가 판정점 2/3 이상 → (i) "V1 이 b\* 보다 적게 실패"; "first arm fewer failures" 2/3 이상 → (ii); POWERED 이고 둘 다 아님 → (iii) "판정하지 못함 (유의 방향 없음)"; UNDECIDED (power guard 미달) → (iv) "판정하지 못함 (검정력 미달)". 문장: (i) 이면 "이 채널·변조 설정 (UMi 28 GHz 8×4, 16-QAM, K_b 90) 에서 동결 prior 의 재사용과 성능 이득을 함께 확인했다"; (ii)·(iii)·(iv) 이면 "조건에 따라 다른 재사용 범위" 로 쓰고 라벨을 그대로 적는다. GMM b\* 의 "[K 상한 민감: 외삽 불가]" 한정어 유지.

### 2.2 D2 (보조) — 라벨 없음
방향과 무관하게 효과량 (판정점 a:b, ΣF, R, SNR@0.1 격차 [90 %]) 을 보조표에 보고한다. D2 의 결과가 UMi 의 판정을 대체하지 않는다. UMi 를 먼저 단독으로 보고한다.

### 2.3 쓰지 않는 문구
"변조에 무관하게", "diffusion 만의 장점", "동등", "비열등", QPSK 대비 "변조 효과".

## 3. 미리 적는 예측 (개발·test BLER 미열람; §6 에서 적중 / 빗나감)

1. UMi28 의 고른 격자는 G0 그대로 (옮기지 않음).
2. UMi28 표 B `b* → V1` 은 (i) — QPSK 와 같은 방향 (단, QPSK 격차가 셋 중 가장 작았다).
3. D2 의 SNR@0.1 격차 (b\* − V1) 의 점추정은 양수. 채점: 점추정 > 0 이면 적중; `gain()` 이 censored ("n/a" 나 "≥" 꼴) 이면 하한이 양수일 때 적중, 그 밖은 "채점 불가".
4. 두 셀 모두 V1 의 질의 범위 밖 비율은 QPSK 의 같은 셀보다 크지 않다. 채점량: 반복 16 (index 15) 에서 7 SNR 에 걸친 (below + above) 합 / finite 합 — 16-QAM ≤ QPSK 이면 적중 (셀마다).

## 4. 선행 작업·검토

- 코드 (Codex 작성 gpt-6.1-sol · high, 사용자 승인 2026-10-17 CDT; worktree `~/t2_wtE5`, 명세 `reviews/spec_qam16_code.md`, 보고 `reviews/20261018-015911-codex_write_qam16.md`, `qam16/REPORT.md`): 커밋 fb5e365d. 정답 사례 (golden-writer, 구현 미열람): K · 성상 · 왕복 PASS (`qam16/golden/check_e5.out`). Codex 교차 검토 (gpt-6-astra · max): 결함 2 → 수정 (Codex, gpt-6-astra · max, 명세 `reviews/spec_qam16_fix1.md`; 커밋은 Claude 검토 뒤 — §5 에 커밋 번호).
- Claude 가 쓸 것: `qam16/select_grid.py` · `qam16/run_grid.sh` (§1.2; 개발 BLER 전 커밋), `code/e5_compare.py` (§1.4 분석) · `code/run_e5.sh` (§1.4 실행·수용·sha 대조) (동결 = 실행 커밋 전). 분석·실행 코드는 Codex 가 검토한다 (역할 규칙: 쓰지 않은 쪽이 검토).
- 적대적 검토 1 회 (Fable 5.1 subagent): v1 (b885a69f) → MUST 2 · SHOULD 9 · NIT 5 전부 반영 = v2.

## 5. 평가 전 고정 기록 (개발; test 미사용)

(셀마다: G0 의 b\* 개발 실패 수, 안쪽 조건, 옮김 여부와 결과, 최종 7 SNR; ν_q 진단 표 (16-QAM · QPSK); 스모크 RSS → G · 청크 시간 · 추정 총시간; D2 시작 규칙 판단; 코드 커밋; 동결 = 실행 커밋)

기록 2026-10-18 13:55 CDT (Opus 5.5). 원본: `qam16/select_grid_{U28,D2}.out`, `qam16/nuq_summary_{U28,D2}.out` (출력 그대로), 로그 `logs/e5_grid.log` · `logs/run_D2_{U28,D2}QAM16g.log` · `logs/nuq_*.log` · `logs/e5_smoke_{D2,U28}.log`. **test 시행 (0..2559) 은 어느 단계에서도 쓰지 않았다.** 코드 커밋: fb5e365d (Codex, `--mod`) → 57eb1f22 (runner 결함 2 수정 + e5_compare · run_e5.sh) → 2e02fda0 (Codex 교차 검토 결함 2: e5_compare · run_e5.sh 만; `git diff 57eb1f22 2e02fda0 -- conf/code Demo` 는 이 두 파일뿐 — runner 같음).

- **SNR 격자 (§1.2; 개발 시행 5120..5439, b\* 만)**:
  - UMi28 (`run_grid.sh U28`, 10-17 14:23 CDT 시작, CPU 115–117, raw `raw_U28QAM16g` 224 청크 = 7 × 32, run|git 57eb1f22): b\* 실패 / 320 = +3 213 (0.665625), +6 129, +9 92, +12 68, +15 40, +18 23, +21 11 (0.034375); raise 0. 안쪽 조건 (BLER(+3) > 0.1, BLER(+21) < 0.1) 충족 → **G0 = {3, 6, 9, 12, 15, 18, 21} dB** (옮기지 않음).
  - D2 (`run_grid.sh D2`, 15:02 → 15:31 CDT, CPU 118–119, raw `raw_D2QAM16g` 224 청크, run|git 2e02fda0): +3 150 (0.46875), +6 78, +9 48, +12 42, +15 32 (0.1), +18 22, +21 16 (0.05); raise 0. 안쪽 조건 충족 → **G0** (옮기지 않음).
- **ν_q 진단 (§1.3; 개발 시행 5440..5479, n 40, 보고 전용; `qam16/run_nuq_{U28,D2}.sh`, 끝 NUQ_D2_DONE 10-17 15:43 CDT, NUQ_U28_DONE 16:54 CDT)** — 반복 16 의 학습 σ 범위 밖 / finite, 7 SNR (+3 … +21):

  | 셀 · 변조 | +3 | +6 | +9 | +12 | +15 | +18 | +21 | 합 |
  |---|---|---|---|---|---|---|---|---|
  | UMi28 16-QAM | 0/40 | 0/40 | 0/40 | 0/40 | 7/40 | 23/40 | 40/40 | 70/280 = 0.250 |
  | UMi28 QPSK | 0/40 | 0/40 | 0/40 | 0/40 | 8/40 | 39/40 | 40/40 | 87/280 = 0.311 |
  | D2 16-QAM | 0/40 | 0/40 | 0/40 | 0/40 | 27/40 | 26/40 | 40/40 | 93/280 = 0.332 |
  | D2 QPSK | 0/40 | 0/40 | 0/40 | 0/40 | 37/40 | 37/40 | 40/40 | 114/280 = 0.407 |

  (QPSK 행은 같은 시행 **번호**의 QPSK 스트림 — 채널 실현은 다르다, §0. 반복별 비율은 `nuq_summary_*.out`.)
- **메모리·시간 스모크 (§1.4; 격자 4 번째 SNR +12 dB, 개발 시행 5480..5519, 다섯 arm, 1 스레드, fits = test 폴더 바이트 복사본 (스크립트가 cmp))**:
  - D2: `CUDA_VISIBLE_DEVICES= taskset -c <1 CPU> python results/review_next/qam16/rss_smoke_e5.py D2 12` (tmux `e5smokeD2`, 10-17 15:58 → 16:00 CDT, run|git 2e02fda0; meta kron_K 1024 · ll_val|kron −11.459169831224418): 청크 128 s, wall 134 s, **최대 RSS 0.877 GB → G = 1.0**.
  - UMi28: `… nice -n 10 taskset -c 190 … rss_smoke_e5.py U28 12` (tmux `e5usmoke`, 10-18 13:46 → 13:50 CDT, run|git 2e02fda0; meta kron_K 4096 · ll_val|kron 5.797910431000217 · modulation 16qam · payload_bits 90 · protocol E5-qam16-v1): 청크 245 s, wall 247 s, **최대 RSS 1.203 GB → G = 1.5**.
  - 스모크 raw 의 BLER 은 열지 않았다 (runner 는 16-QAM 에서 BLER 을 찍지 않는다).
- **워커·시간 추정**: 허용 CPU `24-47,120-143,72-95,168-191` (96 스레드; 다른 등록 runner 와 동시에 돌리지 않는다 — run_e5.sh 가 거부). MemAvailable 1003263876 kB (10-18 13:51–13:53 CDT 사이, SBL32 §5 와 같은 측정) → ⌊0.8 · 956.8 / G⌋ = 510 (UMi) · 765 (D2) → 워커 = 96. 총시간 ≈ ⌈448 / 96⌉ × t = 5 × 245 s ≈ 20 min (UMi), 5 × 128 s ≈ 11 min (D2) (단독 1 스레드 청크 시간; 경합 미반영).
- **D2 시작 규칙 (§1.5)**: UMi 종료 (예상 10-18 ~ 10-19 CDT) + D2 추정 11 min ≪ 2026-10-24 06:00 CDT → D2 를 UMi 다음에 시작한다. 규칙은 실제 UMi 종료 시각에 다시 적용해 §6 에 적는다 (Codex 교차 검토 B 의 확인 필요).
- **시작 명령 (§1.4)**: `E5_CPUS=24-47,120-143,72-95,168-191 bash code/run_e5.sh U28` → 끝난 뒤 `E5_CPUS=24-47,120-143,72-95,168-191 bash code/run_e5.sh D2` (tmux; main 실행 커밋에서).
- `qam16/e5_s5.txt` (실행 커밋에서 main 에 더한다): `FREEZE <동결 커밋>` / `GRID_U28 3 6 9 12 15 18 21` / `GRID_D2 3 6 9 12 15 18 21` / `WGB_U28 1.5` / `WGB_D2 1.0`.
- **실행 커밋 (2026-10-18 14:28 CDT, main)**: 이 문서 · `qam16/e5_s5.txt`: FREEZE d6a76fbf / GRID_U28 3 6 9 12 15 18 21 / GRID_D2 3 6 9 12 15 18 21 / WGB_U28 1.5 / WGB_D2 1.0 를 더하는 커밋. FREEZE d6a76fbf = e3-sbl32 (73282a1e) 와 e5-qam16 (83b7f4f6) 를 main 에 병합한 커밋 (code/ 는 두 브랜치의 자동 병합 — arms.py · runner.py 는 겹치지 않는 hunk). 병합 확인 (`results/review_next/merge_check_e3e5.sh`, 10-18 14:23 → 14:27 CDT, git d6a76fbf, 로그 `logs/merge_check_e3e5.log`): 세 개발 스모크 청크 (SBL 4160..4199 0 dB · E5 UMi · D2 5480..5519 +12 dB) 를 병합 코드로 다시 돌려 브랜치 청크와 데이터 배열 16 · 43 · 43 개 모두 바이트 동일. `pair_baselines.py` 를 main 에서 기록 인자 (`--r0 at1`, 기존 raw 절대경로, ALD 는 main 복사본) 로 다시 돌린 출력 = t2_wtS `pairB_U28NR32B16e4.txt` (경로가 적힌 머리 줄 외 바이트 동일). 세 실행은 `results/review_next/run_e3e5_chain.sh` 가 차례로 띄운다 (SBL32 → E5 UMi → E5 D2; 각 스크립트가 다른 runner 가 돌면 거부).

## 6. 결과 (이 절은 추가만 한다)

### 6.1 실행 기록 (기록 2026-10-18 15:38 CDT, Opus 5.5 — 원자료 전사; 판정은 6.2)

- **실행**: 실행 커밋 13f05fb1 (FREEZE d6a76fbf; `git diff d6a76fbf 13f05fb1 -- conf/code Demo` 0), tmux `e3e5` 의 `run_e3e5_chain.sh` 둘째 · 셋째 단계 (첫 단계 SBL32 는 14:45 CDT 에 끝남). `logs/run_e5.log`: UMi 10-18 14:45 CDT start (resume=0, grid 3…21, WGB 1.5, CPUs 24-47,120-143,72-95,168-191) → 15:18 CDT runner exit 0 → accept_eval OK · accept_raw OK · compare OK → **E5_DONE U28 ok=3 fail=0**; D2 시작 규칙 (`logs/run_e3e5_chain.log`: 15:18 CDT "now + 11 min <= 2026-10-24 06:00 CDT" OK) → D2 15:18 CDT start (WGB 1.0) → 15:36 CDT runner exit 0 → 세 단계 OK → **E5_DONE D2 ok=3 fail=0**. 재개 없음.
- **runner**: UMi 메모리 가드 529 → 워커 96, 448 청크, 32.5 min, 청크 평균 388 s · 중앙 397 s (252–446); D2 793 → 96, 448, 17.7 min, 평균 213 s · 중앙 225 s (121–244) (`logs/run_D2_{U28,D2}QAM16.log` :6, :7, :456). 모든 청크 "arm-trial exceptions=0".
- **raw** `raw_U28QAM16/` · `raw_D2QAM16/` 각 448 npz; 값 집합 (두 폴더): `run|git` {13f05fb1}, `meta|modulation` {16qam}, `meta|payload_bits` {90}, `meta|protocol` {E5-qam16-v1}, `meta|bstar` {kron}, `run|iters` {16}, `run|seed` {20260926}, `meta|ntrain` {160000.0}, `meta|jobs` {96}; UMi `meta|kron_K` {4096} · `ll_val|kron` {5.797910431000217} · `worker_gb` {1.5} · stagec id sha256[:16] 6f3a1b9490864af1 role=best; D2 {1024} · {−11.459169831224418} · {1.0} · 4443921ce8d5c4a1 (epoch 1784, best 1764). 다섯 arm 모두 raise 0 (896 청크 어디에도 `<arm>|failed` 키가 없고, runner 로그 896 줄 모두 "arm-trial exceptions=0"; 실패 수 계산은 비유한 blk_err 를 실패로 센다).
- **수용**: `qam16/U28QAM16_accept.txt` · `D2QAM16_accept.txt` "ACCEPT: OK"; accept_raw (448 청크 run|git · meta · 다섯 arm × KEYS_RAW (40, 16)) OK. `e5_compare` 검사 줄: 7 점, n = 2560, 다섯 arm, 16qam / 90 / E5-qam16-v1, load_raw WARNING 없음.

### 6.2 결과 (`qam16/compare_U28QAM16.txt` · `compare_D2QAM16.txt`)

**UMi28 (주검증) — 표 B `b* → V1`** (앵커 b\*): 판정점 **+12 · +15 · +18 dB**; 부호검정 @16 +12 dB 72:17 (p 3.2e-09), +15 dB 49:20 (6.4e-04), **+18 dB 4:1666 (p ≈ 0)**, pooled 125:1703; POWERED; "second arm fewer failures at 2/3 points, first arm fewer failures at 1/3 points -> significant". SNR@0.1 격차: "n/a (16.03 vs >  21) — extend the SNR grid" (V1 이 격자에서 BLER 0.1 아래로 내려가지 않는다: +15 dB 277/2560 = 0.108). 판정점 ΣF b\* 1004 · V1 2582 · genie 438 → R = −2.787986 [90 % −3.027, −2.572].

- **등록 규칙 (§2.1) 을 기계적으로 적용한 라벨 = (i)** ("second arm fewer failures" 2/3 ≥ 2/3) + GMM b\* 한정어 "[K 상한 민감: 외삽 불가]" (§2.1, §1.1 UMi b\* kron K 4096 = 격자 끝). **해석 쟁점 (사용자 결정 — 아래 6.4)**: §2.1 의 규칙은 판정점별 유의 방향의 개수만 보고 크기 (ΣF · R) 는 보지 않는다 — 셋째 판정점 +18 dB 에서 V1 이 붕괴 (b\* 만 실패 4 : V1 만 실패 1666), 판정점 합 실패 V1 > b\* (2582 vs 1004), R < 0, 격차는 정의되지 않음. (i) 의 등록 문장 ("동결 prior 의 재사용과 성능 이득을 함께 확인했다") 을 쓸지, 다른 문장으로 보고할지는 정하지 않았다.
- 7 SNR 실패 수 / 2560 (V1 · b\* · R2 · genie · V1-pilot): +3 1549 · 1560 · 1669 · 1054 · 1755; +6 1022 · 1060 · 1168 · 704 · 1107; +9 718 · 753 · 868 · 428 · 761; +12 461 · 516 · 611 · 246 · 501; +15 277 · 306 · 384 · 136 · 293; **+18 1844** · 182 · 243 · 56 · 171; **+21 2543** · 107 · 142 · 29 · 91.
- 같은 출력의 다른 쌍 (table_B 자체 목록, 라벨 없음): R2 → b\* 214:40 (+15 · +18 · +21; b\* 3/3, 격차 +1.63 dB [+1.22, +2.19]); b\* → genie 776:11 (+9 · +12 · +15; +4.25 dB [+3.63, +4.87]); R2 → V1 128:4023 (+15 · +18 · +21; V1 적게 1/3, R2 적게 2/3; 격차 n/a); V1 → genie 657:11 (+9 · +12 · +15; ≥ +9.22 dB, V1 이 0.1 에 닿지 않음).
- 보고 전용 `b* → V1-pilot` (라벨 없음; +12 · +15 · +18): 50:35 · 41:28 · 33:22, pooled 124:85; POWERED, 어느 점도 유의하지 않음 → not significant; 격차 +0.28 dB [+0.06, +0.53].

**D2 (보조, 라벨 없음 — §2.2)** — `b* → V1` (앵커 b\*): 판정점 +9 · +12 · +15 dB; 157:23 · 121:17 · 93:16, pooled 371:56; POWERED, V1 적게 3/3; SNR@0.1 격차 **+3.44 dB [+2.62, +4.33]**; ΣF b\* 922 · V1 607 · genie 465 → R = 0.689278 [0.642, 0.736]. 판정점 밖에서 V1 붕괴: 실패 수 V1 +18 dB **2485**, +21 dB **2557** / 2560 (b\* 147 · 123). 7 SNR (V1 · b\* · R2 · genie · V1-pilot): +3 828 · 1189 · 1336 · 546 · 1000; +6 470 · 675 · 831 · 317 · 503; +9 286 · 420 · 522 · 217 · 307; +12 184 · 288 · 361 · 140 · 187; +15 137 · 214 · 285 · 108 · 135; +18 2485 · 147 · 202 · 75 · 97; +21 2557 · 123 · 166 · 49 · 72. 보고 전용 `b* → V1-pilot`: 144:31 · 116:15 · 92:13, pooled 352:59, V1-pilot 적게 3/3, 격차 +3.09 dB [+2.34, +3.87].

### 6.3 예측 채점 (§3)

1. **적중** — UMi28 격자 G0 (옮기지 않음; §5).
2. **적중 (기계적)** — UMi28 표 B 라벨 규칙의 출력 = (i). 단 6.2 의 해석 쟁점 (셋째 판정점의 반대 방향 붕괴) 이 걸려 있다.
3. **적중** — D2 SNR@0.1 격차 (b\* − V1) 점추정 +3.44 dB > 0 (censored 아님).
4. **적중** — 두 셀 모두 반복 16 의 범위 밖 비율 16-QAM ≤ QPSK (UMi 70/280 = 0.250 ≤ 87/280 = 0.311; D2 93/280 = 0.332 ≤ 114/280 = 0.407; 개발 시행 5440..5479, §5).

### 6.4 관찰 (사후, 보고 전용 — 등록 분석 아님; `qam16/traj_report.py` → `qam16/traj_{U28,D2}QAM16.out`)

- 두 셀 모두 **+18 · +21 dB 에서 V1 의 실패가 반복과 함께 늘어난다**: 반복 1 (파일럿만의 추정; V1 = V1-pilot) 의 실패는 genie 를 뺀 네 arm 가운데 가장 적다 (V1 · b\* · R2 · genie — UMi +18: 511 · 542 · 577 · 310; +21: 361 · 382 · 393 · 167 / D2 +18: 503 · 619 · 654 · 459; +21: 460 · 536 · 575 · 398) 인데, 첫 데이터 보조 반복 (반복 2) 에서 이미 UMi +18 1951 · +21 2458, D2 +18 2060 · +21 2336 로 뛰고 반복 16 까지 그 수준 (UMi 1844 · 2543, D2 2485 · 2557). 채널 추정 NMSE 중앙값 (반복 1 → 16): UMi +18 2.90e-3 → 8.18e-2, +21 1.54e-3 → 4.33; D2 +18 1.51e-3 → 2.71e-1, +21 8.16e-4 → 4.59. raise 0.
- 같은 데이터 보조 반복 루프를 쓰는 b\* 와, 반복 중 채널 추정을 고정하는 V1-pilot 은 +18 · +21 dB 에서 반복과 함께 실패가 줄어든다 (`traj_*.out` 의 반복 1 · 2 · 4 · 8 · 16; 16 회 전체에서 늘지 않는다 (단조 비증가, 같은 값이 이어지는 구간 있음) — raw 의 `<arm>|blk_err` 열 합으로 재계산 가능). +15 dB 이하에서는 V1 도 반복과 함께 줄어든다.
- 개발 진단 (§5 ν_q 표, 반복 16, 개발 시행 5440..5479) 에서 V1 질의 잡음이 학습 σ 범위 밖인 비율은 +18 · +21 dB 에서 높다 (UMi 16-QAM 23/40 · 40/40, D2 27/40 (+15) · 26/40 · 40/40). 같은 셀 QPSK 의 개발 진단에서도 범위 밖 비율은 높았다 (UMi +18 39/40, D2 +15 37/40) — QPSK test 는 이 셀들에서 +15 dB 를 넘는 점이 없어 QPSK 고 SNR 에서 같은 일이 생기는지는 모른다. 또 D2 16-QAM +15 dB 는 개발 진단의 범위 밖 비율이 27/40 이지만 test 에서 V1 은 붕괴하지 않았다 (137/2560; V1-pilot 135, b\* 214, R2 285) — 범위 밖 비율 (개발 시행 5440..5479) 과 붕괴 (test 0..2559) 는 시행 집합이 다르며, 같은 SNR 에서 함께 나타나지 않는 경우도 있다.
- **원인은 확인하지 않았다** (가설로도 적지 않는다). 확인하려면 개발 시행으로 따로 진단해야 한다 — 사용자 결정.
- **Codex 독립 분석** (gpt-6-astra · max, 사용자 승인; 질문과 자료 경로만 줌 — `reviews/20261019-054103-prompt_e5_blind.md`): 라벨 (i) 은 규칙대로 맞고 사후에 바꾸면 안 된다, 단 등록 문장을 쓴다면 +18 dB 역전 · 음의 R · V1 이 격자에서 BLER 0.1 에 닿지 않음을 함께 적어야 한다; 16-QAM 의 사후 모멘트 (x̄, v) 경로는 합성 검증에서 결함 없음; 반복 1 성공 → 반복 16 실패 시행 UMi +18 1347 · +21 2183, D2 +18 1985 · +21 2098 (반대 14 · 1 · 3 · 1); 원인은 특정하지 못함 (확신 낮음). 그 밖의 결함 1: UMi28 계열 raw · 표 머리의 학습 arm 예산 문자열이 `N_train=28160000` (runner `learned_budget` 의 정규식이 rung `D2SXUMi28160000` 의 '28' 까지 읽음; 실제 160000) — 표시만 틀리고 BLER · 판정과 무관.

### 6.5 사용자 결정 (2026-10-18 15:59 CDT)

- 사용자 "9 -12 모두 제안대로 하자" (WORK_QUEUE 대기 10 · 11):
  - **UMi28 라벨 · 문장 (대기 10)**: 라벨 (i) 을 그대로 두고 (§2.1, 사후 변경 없음), 등록 문장 뒤에 제한을 붙인다 — "**(i) [K 상한 민감: 외삽 불가]**: 이 채널 · 변조 설정 (UMi 28 GHz 8×4, 16-QAM, K_b 90) 에서 동결 prior 의 재사용과 성능 이득을 함께 확인했다. 단, 이득은 판정점 +12 · +15 dB 에서이며, 셋째 판정점 +18 dB 에서는 V1 이 b\* 보다 크게 더 실패했다 (b\* 만 실패 4 : V1 만 실패 1666; 판정점 합 R = −2.79 [90 % −3.03, −2.57]); V1 은 평가 격자 (+3 … +21 dB) 어디에서도 BLER 0.1 아래로 내려가지 않았다 (+18 · +21 dB 실패 1844 · 2543 / 2560)." D2 (보조) 는 §2.2 대로 효과량 (+9 · +12 · +15 dB, +3.44 dB [+2.62, +4.33], R 0.689) 과 판정점 밖 붕괴 (+18 · +21 dB 2485 · 2557 / 2560) 를 함께 적는다.
  - **원인 진단 (대기 11)**: 개발 시행으로만 진단한다 (Codex 제안 ① 궤적 기록 ② 저장 질의의 denoiser · Jacobian 독립 대조 ③ 필요하면 대조 arm). 결과는 등록 밖 진단으로 따로 기록하고, 이 등록의 test 결과 · 라벨은 바꾸지 않는다.
